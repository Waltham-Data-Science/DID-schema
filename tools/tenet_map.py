#!/usr/bin/env python3
"""The tenet -> class map: which classes each of Brainstorm J's 14 tenets shaped.

WHY THIS IS A CURATED TABLE AND NOT A DERIVATION. The link from a tenet to the
classes it shaped exists only in prose, and it is not recoverable mechanically:

    T-references across schemas/*.md   353
    built schema files naming a tenet    0 of 245

Nothing in the built tree records which tenet produced which decision, so any
"derivation" would be a keyword search dressed up as evidence -- a tenet number
occurring in the same paragraph as a class name is not a claim that the tenet
shaped the class. The table below is therefore HAND-PICKED, and every row pays
for itself with a citation: a plan document plus an ANCHOR, a verbatim string
that must occur in it. The generator locates the anchor, records the file, the
line number and the line, and REFUSES TO EMIT if it cannot. A row nobody can
substantiate is dropped from the table, not softened -- an unsupported tenet
claim in front of a reader is worse than a shorter table.

THREE THINGS THIS TOOL DOES THAT A ROW-COUNTER WOULD NOT:

  1. It states its denominator: 14 tenets declared, N with at least one row, and
     it NAMES the tenets with none. A tenet rendering as an empty panel and a
     tenet nobody has mapped look identical in a viewer; they are not the same
     fact, and the one that is unmapped is the one worth knowing about.

  2. Every class name in every row is checked against three registers -- the
     ledger's v1 source universe, the built V_eta index, and the text of the
     cited document. A name in none of them is a typo or an invention and stops
     the generator. This is also what keeps a DECIDED-but-unbuilt target
     (`acquisition_layout`) honest: it is not in the built tree, so it must at
     least be named by the document that decided it, and the artifact records
     which register vouched for it so the viewer can say so.

  3. IT RUNS A NEGATIVE CONTROL BEFORE IT TRUSTS ITSELF. The substantiation
     lookup is the whole instrument here; a lookup that matched everything
     would substantiate every row including the wrong ones, and would look
     exactly like a lookup that works. So the generator asks it for a canary
     string that cannot occur in any document, and exits non-zero if the lookup
     claims to have found it. `tools/check_vacuous_tests.py` exists in this
     repository because instruments that measure nothing pass quietly.

Usage:  python3 tools/tenet_map.py [--check]
  (no args)  regenerate web/public/tenets.json
  --check    regenerate in memory and exit non-zero if the committed copy differs
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SCHEMAS = REPO / "schemas"
TENETS_DOC = SCHEMAS / "V_eta_tenets.md"
LEDGER = SCHEMAS / "V_eta_coverage_ledger.json"
VETA_INDEX = SCHEMAS / "V_eta" / "index.json"
OUT = REPO / "web" / "public" / "tenets.json"

TENET_IDS = [f"T{i}" for i in range(1, 15)]

# A string that cannot occur in a plan document, used to ask the substantiation
# lookup whether it is capable of saying no. Not a constant anyone should ever
# have a reason to change -- if it is ever found, the finder is broken.
CANARY = "ZZ-NO-SUCH-ANCHOR-8f21c4-DO-NOT-ADD-THIS-STRING-TO-ANY-DOCUMENT"


class Row:
    """One curated tenet -> classes mapping, with the citation that carries it.

    tenet    T1..T14
    change   the one-line before/after, in the tenet's own terms
    before   the did_v1 (or superseded V_eta) classes as they stood
    after    what they became
    doc      the plan document that substantiates the row, relative to schemas/
    anchor   a VERBATIM string that must occur in `doc`; the generator quotes
             the line it lands on, so the reader sees the source sentence and
             not a paraphrase of it
    note     optional extra context for the reader (never evidence)
    """

    def __init__(self, tenet, change, before, after, doc, anchor, note=""):
        self.tenet = tenet
        self.change = change
        self.before = before
        self.after = after
        self.doc = doc
        self.anchor = anchor
        self.note = note


# ---------------------------------------------------------------------------
# THE CURATED TABLE. Add a row only with a citation you have read.
# ---------------------------------------------------------------------------
TENET_MAP = [
    Row("T1",
        "The recording element stops being its own kind of thing and becomes a "
        "plain subject with its id preserved; what it IS becomes a term "
        "assertion and where it came from becomes an edge.",
        ["element"],
        ["subject", "term_assertion", "directed_relation"],
        "V_eta_ensemble_plan.md",
        "element→subject, id preserved, Path-S",
        "T1 admits no kind-subclasses, so a probe, a neuron and an animal are "
        "all subjects; the difference is what the graph and the ontology say "
        "about them."),
    Row("T1",
        "The recording rig is NOT promoted to a subject. `acquisition_system` "
        "sits beside `software` and `session` under `entity`, because T1's "
        "bare subject is the thing statements are ABOUT and a rig is what does "
        "the recording.",
        ["daqsystem"],
        ["acquisition_system"],
        "V_eta_daq_family_decisions.md",
        "T1's bare subject is the thing statements are",
        "The tenet is doing negative work here -- it is the reason a class was "
        "kept OFF the subject spine."),
    Row("T2",
        "`validity` was the only data_type naming a SEMANTIC rather than a kind "
        "of value. The semantic moved onto `subject_statement.variable`, where "
        "T2 puts identity, and the class became the plain boolean type.",
        ["validity", "validity_observation"],
        ["logical", "logical_observation"],
        "V_eta_logical_observation_plan.md",
        "The semantic belongs in `subject_statement.variable`.",
        "T2's 'identity rides on `variable`, not the class' is what makes one "
        "query span every statement; a class per semantic breaks it."),
    Row("T3",
        "One raster type crossed with the statement direction gives the "
        "measured case and the shown-as-stimulus case, instead of two "
        "unrelated image classes.",
        ["imageStack", "image"],
        ["image", "image_observation", "image_manipulation"],
        "V_eta_image_model_plan.md",
        "**Two directions** (T3):",
        "T3 is the factoring move: data_type x direction, so a new stance on "
        "an existing value costs a leaf, not a design."),
    Row("T4",
        "An ensemble's membership stops being a list inside a document and "
        "becomes epoch-scoped `member_of` edges -- documents in their own "
        "right, with the per-epoch roster preserved in the graph.",
        ["ensemble"],
        ["subject", "directed_relation", "sampled_body"],
        "V_eta_ensemble_plan.md",
        "T4: relations are documents",
        "The per-epoch map document dissolves: once each spike train is keyed "
        "by its neuron-subject id, the column legend carries nothing."),
    Row("T5",
        "The daq family does NOT earn subjecthood: the payload is a MATLAB "
        "class name, so there is no hardware fact in the document to attach to "
        "a device-subject, and T5 declines to mint one.",
        ["daqsystem", "daqreader"],
        ["acquisition_system", "software"],
        "V_eta_daq_family_decisions.md",
        "does not license minting one",
        "Path S in its refusing mode -- the test is whether the structure is a "
        "thing-in-itself, not whether a name exists for it."),
    Row("T6",
        "A labeled N-D numeric grid is a CARRIER, not a value type: `ngrid` "
        "phases into `sampled_body`, and the generic `array` composite that "
        "would have duplicated it was killed outright.",
        ["ngrid"],
        ["sampled_body"],
        "V_eta_image_model_plan.md",
        "**`ngrid` → phases into `sampled_body`**",
        "`sampled_body` is already self-describing (axis + typed datum), which "
        "is exactly what a bare numeric grid is."),
    Row("T6",
        "`zarr` is deleted rather than migrated -- a storage format is a field "
        "on a body, not a class, and this one has no v1 source to migrate.",
        ["zarr"],
        ["sampled_body", "opaque_body"],
        "V_eta_data_body_model_plan.md",
        "`zarr` is DELETED, not migrated",
        "T6's 'encoding/format is a field, not a class', applied to the one "
        "carrier that never had a did_v1 document behind it."),
    Row("T7",
        "A raw recording becomes an observation OF THE SPECIMEN taken WITH the "
        "electrode: the loose `probe observes specimen` relation is replaced by "
        "an `instrument_id` edge, and the modality typing the bare-body path "
        "dropped comes back.",
        ["element", "element_epoch"],
        ["voltage_observation", "sampled_body", "acquisition_epoch"],
        "V_eta_recording_observation_plan.md",
        "the `probe observes specimen` relation is REPLACED by the `instrument_id` edge",
        "T7's two questions: whose value is this (subject_id) and what tool "
        "produced it (instrument_id). The electrode is a subject -- just not "
        "the subject of this statement."),
    Row("T8",
        "Three `dataset` fields that were free `char` become `ontology_term` "
        "values bound to openMINDS term sets through a new binding shape keyed "
        "by (class, field) rather than by a sibling `variable`.",
        ["dataset"],
        ["dataset", "binding_registry_meta"],
        "V_eta_openminds_controlled_terms_binding_plan.md",
        "(new) `entity_field_bindings`** — keyed by **(class, field)**",
        "T8 is about hard validation, and the binding shape follows the thing "
        "being validated: an entity field names its own term set."),
    Row("T9",
        "A strain stops being a string inside somebody else's document and "
        "becomes a first-class entity with a repeatable `global_identifier`, "
        "reached by a typed `strain_id` edge.",
        ["openminds_subject"],
        ["strain", "term_assertion"],
        "V_eta_openminds_family_record.md",
        "So the edge to a `strain` document is `strain_id`",
        "T9's FAIR entities are what make the openMINDS crosswalk mechanical "
        "rather than per-dataset."),
    Row("T10",
        "Every tuning calculator output folds 1->1 into ONE calculation leaf "
        "with `base.id` and `depends_on` preserved -- never dissolved into "
        "observations, because dissolution dangles every downstream reference.",
        ["oridirtuning_calc", "contrast_tuning_calc",
         "spatial_frequency_tuning_calc", "temporal_frequency_tuning_calc",
         "speed_tuning_calc", "tuningcurve_calc"],
        ["tuning_curve_calculation", "subject_calculation"],
        "V_eta_tuning_model_plan.md",
        "ONE `tuning_curve_calculation` leaf** (id-preserving 1→1 fold)",
        "The 11,448-orphan run is what this tenet is made of: id preservation "
        "plus existence-only `must_refer` is why the calculators un-defer with "
        "0 orphans."),
    Row("T11",
        "The independent variable of a tuning curve is a `variable`, not a "
        "name suffix -- so `orientation_tuning_curve`, `contrast_tuning_curve` "
        "and their three siblings were never minted.",
        ["orientation_direction_tuning", "contrast_tuning",
         "spatial_frequency_tuning", "temporal_frequency_tuning",
         "speed_tuning"],
        ["tuning_curve"],
        "V_eta_tuning_model_plan.md",
        "`subject_statement.variable`, **not** a name suffix (T11) — so we do NOT mint",
        "T11 says the name encodes only the data type and the stance. An "
        "independent variable is neither."),
    Row("T11",
        "The infra tier is not exempt from the grammar: R5 strips "
        "`binary`/`series`/`parameters` from the acquisition layout class. "
        "A DECIDED TARGET, NOT BUILT -- the walkthrough re-opened the whole "
        "infra tier and a build was reverted pending review.",
        ["binaryseries_parameters"],
        ["acquisition_layout"],
        "V_eta_tenet_audit.md",
        "`binaryseries_parameters` → **`acquisition_layout`**",
        "Rendered because it is the tenet's live edge, not because it is done: "
        "the target does not exist in the built tree and the artifact says so. "
        "The same R5 line names three further renames; only this one has a "
        "source class that is still both a v1 source and a built class."),
    Row("T12",
        "Six overlapping v1 tuning classes and five fit shapes collapse into "
        "ONE `tuning_curve` composite. The curve was identical in all six; only "
        "the fitted model differed, and a model is a controlled term.",
        ["stimulus_tuningcurve", "orientation_direction_tuning",
         "contrast_tuning", "spatial_frequency_tuning",
         "temporal_frequency_tuning", "speed_tuning"],
        ["tuning_curve", "tuning_curve_calculation"],
        "V_eta_tuning_model_plan.md",
        "ONE `tuning_curve` `data_type` composite",
        "T12's parsimony test: a new composite is warranted only by a new "
        "quantity dimension or a new measurement structure. Five names for one "
        "curve is neither."),
    Row("T12",
        "The five fit shapes become an ARRAY of `model_fit` entries "
        "distinguished by a bound `model` term -- not a class per fit, and not "
        "a single slot that would silently drop four of the five.",
        ["fitcurve"],
        ["tuning_curve"],
        "V_eta_tuning_model_plan.md",
        "not a class per fit",
        "The array is the re-audit's correction: spatial and temporal "
        "frequency tunings each carry five co-existing fits."),
    Row("T13",
        "`app` loses to `software`: the abbreviation is not the more "
        "recognizable form, and in a neuroscience corpus `application` "
        "collides with applying a stimulus. The mixin copied into every "
        "calculator output becomes a deduplicated entity behind an edge.",
        ["app"],
        ["software"],
        "V_eta_tenet_audit.md",
        "`app` → `software` entity + `software_id` edge + `execution_environment`",
        "T13's abbreviation rule, and T9's entity rule, landing on the same "
        "class from two directions."),
    Row("T13",
        "`control_stimulus_ids` drops the `ids` container word and becomes "
        "`control_designation` -- a name for the content, not for the box the "
        "content came in.",
        ["control_stimulus_ids"],
        ["control_designation"],
        "V_eta_tenet_audit.md",
        "`control_stimulus_ids` → **`control_designation`** (drops the `ids` container word, T13)",
        "The same rule kills `parameters`, `data`, `info`, `table`, `record` "
        "and `metadata` wherever they name a class."),
    Row("T13",
        "The `derived_summary` bag was killed and replaced by three sub-blocks "
        "named for what they hold; an untyped `{name, value}` bag is the "
        "field-level form of naming the container.",
        ["orientation_direction_tuning"],
        ["tuning_curve"],
        "V_eta_tenet_audit.md",
        "the `derived_summary` bag is KILLED",
        "`significance` / `circular_statistics` / `interpolated_values` -- and "
        "they stay typed and queryable, which the bag would have cost."),
    Row("T14",
        "`image` carries its pixels in exactly one `value` slot, with dtype, "
        "axes, colour model and channels declared INSIDE the cell beside them "
        "-- because dtype is not recoverable from an inline matrix.",
        ["imageStack"],
        ["image", "image_observation", "image_manipulation"],
        "V_eta_tenet_audit.md",
        "one `value` cell (T14)",
        "One payload slot is what makes T3's factoring mechanical: `mass.value` "
        "means the same thing under every direction."),
    Row("T14",
        "The named composite types shipped for most of the project as bare enum "
        "strings whose real layout lived in migrator literals, and 26 of 35 "
        "composites emitted no query path at all. Declaring the cell inline is "
        "what made the values indexable.",
        ["stimulus_tuningcurve"],
        ["tuning_curve", "voltage", "image"],
        "V_eta_tenet_audit.md",
        "26 of 35",
        "T14 is T8 one level down: T8 governs the vocabulary a value may take, "
        "T14 governs the value's own shape."),
]


# ---------------------------------------------------------------------------
# Substantiation
# ---------------------------------------------------------------------------
def read_doc(name):
    """Read a plan document under schemas/. Missing is a hard error: a row
    citing a document that does not exist is exactly the state this generator
    exists to make impossible."""
    path = SCHEMAS / name
    if not path.is_file():
        raise FileNotFoundError(
            f"cited document does not exist: schemas/{name}")
    return path.read_text(encoding="utf-8")


def find_anchor(text, anchor):
    """Locate a verbatim anchor. Returns [(line_no, line_text), ...].

    THE ONE INSTRUMENT IN THIS TOOL. Everything else is bookkeeping; this is
    what decides whether a row is evidence or an assertion. It is deliberately
    a literal substring search over lines: no regex, no fuzzy match, no
    normalisation. A lookup that is clever enough to nearly-match is clever
    enough to match a row that is wrong.
    """
    hits = []
    for i, line in enumerate(text.splitlines(), start=1):
        if anchor in line:
            hits.append((i, line.strip()))
    return hits


def negative_control(docs):
    """Ask the lookup for a string that cannot be there, over every cited
    document. A lookup that answers yes here would substantiate anything."""
    found = []
    for name, text in docs.items():
        if find_anchor(text, CANARY):
            found.append(name)
    return found


# ---------------------------------------------------------------------------
# Tenet text, read from the north star rather than retyped here
# ---------------------------------------------------------------------------
HEAD = re.compile(r"^###\s+(T\d{1,2})\s+—\s+(.*)$")


def parse_tenets(text):
    """Pull `### T<n> — <title>` sections out of V_eta_tenets.md.

    The statement of a tenet is quoted from the north-star document, never
    retyped into this file: a paraphrase drifting away from the tenet it claims
    to render is the same failure as a plan document's header drifting away
    from its own sign-off.
    """
    lines = text.splitlines()
    starts = []
    for i, line in enumerate(lines):
        m = HEAD.match(line)
        if m:
            starts.append((i, m.group(1), m.group(2).strip()))
    out = {}
    for idx, (i, tid, title) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        body = "\n".join(lines[i + 1:end]).strip()
        out[tid] = {"id": tid, "title": title, "statement": body,
                    "line": i + 1}
    return out


# ---------------------------------------------------------------------------
# Class-name registers
# ---------------------------------------------------------------------------
def registers():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    v1 = {r["v1_class"] for r in ledger["rows"]}
    v1 |= {r["veta_class"] for r in ledger["rows"] if r.get("veta_class")}
    index = json.loads(VETA_INDEX.read_text(encoding="utf-8"))
    built = {e["class_name"] for e in index["schemas"]}
    return v1, built


def classify(name, v1, built, doc_text):
    """Where a class name is vouched for. Empty list => unsubstantiated."""
    where = []
    if name in v1:
        where.append("v1_source")
    if name in built:
        where.append("built")
    if re.search(r"(?<![\w])" + re.escape(name) + r"(?![\w])", doc_text):
        where.append("named_in_cited_plan")
    return where


# ---------------------------------------------------------------------------
def build(table=None, doc_reader=None, finder=None):
    """Assemble the artifact.

    `table`, `doc_reader` and `finder` are injectable so the tests can mutate
    one part at a time -- a bad row, a missing document, a lookup that matches
    everything -- and prove each reddens on its own.
    """
    table = TENET_MAP if table is None else table
    doc_reader = read_doc if doc_reader is None else doc_reader
    finder = find_anchor if finder is None else finder

    tenets = parse_tenets(TENETS_DOC.read_text(encoding="utf-8"))
    missing_tenets = [t for t in TENET_IDS if t not in tenets]
    if missing_tenets:
        raise ValueError(
            f"V_eta_tenets.md declares no section for {missing_tenets} -- the "
            "north star and this map disagree about which tenets exist")

    v1, built = registers()

    docs = {}
    for row in table:
        if row.doc not in docs:
            docs[row.doc] = doc_reader(row.doc)

    # THE NEGATIVE CONTROL, before a single row is trusted.
    if docs:
        vacuous = negative_control_with(finder, docs)
        if vacuous:
            raise ValueError(
                "SUBSTANTIATION LOOKUP IS VACUOUS: it reported the canary "
                f"string present in {vacuous}. A lookup that matches "
                "everything substantiates every row, including the wrong "
                "ones. Refusing to emit.")

    rows = []
    for row in table:
        if row.tenet not in tenets:
            raise ValueError(
                f"row cites {row.tenet}, which is not a tenet in "
                f"V_eta_tenets.md (declared: {sorted(tenets)})")
        text = docs[row.doc]
        hits = finder(text, row.anchor)
        if not hits:
            raise ValueError(
                f"UNSUBSTANTIATED ROW ({row.tenet}, schemas/{row.doc}): the "
                f"anchor {row.anchor!r} does not occur in the cited document. "
                "Fix the citation or drop the row -- do not soften it.")
        line_no, quote = hits[0]

        classes = {}
        unvouched = []
        for name in list(row.before) + list(row.after):
            where = classify(name, v1, built, text)
            classes[name] = where
            if not where:
                unvouched.append(name)
        if unvouched:
            raise ValueError(
                f"UNKNOWN CLASS NAME(S) in the {row.tenet} row citing "
                f"schemas/{row.doc}: {unvouched}. None is a v1 source, a built "
                "V_eta class, or named in the cited document -- so it is a "
                "typo or an invention.")

        # A NAME VOUCHED FOR BY THE CITED PLAN ALONE IS NOT A CLASS THAT
        # EXISTS. It is either a decided-but-unbuilt target, or a class that
        # has since been superseded or deleted -- and both must be captioned
        # rather than rendered as an ordinary chip. This flag is what caught
        # `dataseries_channel_map`: the R5 rename line still names it as a
        # source, and `a4ae77f` ("delete dataseries_channel_map: no v1
        # provenance, on the team's instruction") removed the class on
        # 2026-08-09, so a panel showing the rename would have shown a rename
        # of nothing.
        plan_only = [n for n, w in classes.items() if w == ["named_in_cited_plan"]]
        rows.append({
            "tenet": row.tenet,
            "change": row.change,
            "before": row.before,
            "after": row.after,
            "after_built": [c for c in row.after if c in built],
            "after_not_built": [c for c in row.after if c not in built],
            "plan_only_classes": plan_only,
            "class_registers": classes,
            "citation": {
                "doc": f"schemas/{row.doc}",
                "line": line_no,
                "anchor": row.anchor,
                "quote": quote,
            },
            "note": row.note,
        })

    by_tenet = {t: [r for r in rows if r["tenet"] == t] for t in TENET_IDS}
    unmapped = [t for t in TENET_IDS if not by_tenet[t]]
    mapped_classes = sorted({c for r in rows for c in r["before"] + r["after"]})

    payload = {
        "title": "Brainstorm J's tenets, and the classes each one shaped",
        "description": (
            "A CURATED map: the link from a tenet to a class exists only in "
            "prose (353 T-references across schemas/*.md; 0 of 245 built "
            "schema files name a tenet), so every row carries the plan "
            "document and the verbatim line that substantiates it. A row that "
            "could not be substantiated was dropped, not softened."),
        "generated_by": "tools/tenet_map.py",
        "tenets_document": "schemas/V_eta_tenets.md",
        "denominator": {
            "tenets_declared": len(TENET_IDS),
            "tenets_with_at_least_one_row": len(TENET_IDS) - len(unmapped),
            "tenets_with_no_substantiated_row": unmapped,
            "rows": len(rows),
            "distinct_classes_named": len(mapped_classes),
            "classes_in_the_built_set": len([c for c in mapped_classes
                                             if c in built]),
            "classes_that_are_v1_sources": len([c for c in mapped_classes
                                                if c in v1]),
            "classes_vouched_only_by_the_cited_plan": sorted(
                {c for r in rows for c in r["plan_only_classes"]}),
            "plan_documents_cited": sorted(f"schemas/{d}" for d in docs),
            "negative_control": (
                "the substantiation lookup was asked for a canary string that "
                "cannot occur in any document and did not find it"),
        },
        "tenets": [tenets[t] for t in TENET_IDS],
        "rows": rows,
        "classes_index": mapped_classes,
    }
    return payload


def negative_control_with(finder, docs):
    found = []
    for name, text in docs.items():
        if finder(text, CANARY):
            found.append(name)
    return found


def serialize(payload):
    return json.dumps(payload, indent=1, sort_keys=True) + "\n"


def print_denominator(payload):
    d = payload["denominator"]
    print(f"DENOMINATOR: {d['tenets_declared']} tenet(s) declared in "
          f"schemas/V_eta_tenets.md, {d['tenets_with_at_least_one_row']} with "
          f"at least one substantiated row, {d['rows']} row(s) total, "
          f"{d['distinct_classes_named']} distinct class(es) named, "
          f"{len(d['plan_documents_cited'])} plan document(s) cited")
    unmapped = d["tenets_with_no_substantiated_row"]
    if unmapped:
        # NAMED, not counted. A tenet with no row renders as an empty panel,
        # which is indistinguishable from a tenet that shaped nothing.
        print(f"  TENETS WITH NO SUBSTANTIATED ROW ({len(unmapped)}): "
              f"{', '.join(unmapped)} -- these render as UNMAPPED in the "
              "viewer, not as empty")
    else:
        print("  tenets with no substantiated row: 0")
    print(f"  classes: {d['classes_that_are_v1_sources']} are v1 sources, "
          f"{d['classes_in_the_built_set']} are in the built V_eta set, "
          f"{len(d['classes_vouched_only_by_the_cited_plan'])} are vouched for "
          "by the cited plan ALONE (decided-but-unbuilt, or superseded): "
          f"{', '.join(d['classes_vouched_only_by_the_cited_plan']) or 'none'}")
    print(f"  negative control: {d['negative_control']}")


def main(argv):
    check = "--check" in argv
    payload = build()
    print_denominator(payload)
    text = serialize(payload)
    if check:
        if not OUT.exists():
            print(f"FAIL: {OUT.relative_to(REPO)} does not exist -- run "
                  "`python3 tools/tenet_map.py`")
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print(f"FAIL: {OUT.relative_to(REPO)} is STALE -- regenerate it "
                  "(`python3 tools/tenet_map.py`) and commit the result")
            return 1
        print(f"OK: {OUT.relative_to(REPO)} matches the generated content")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"WROTE {OUT.relative_to(REPO)} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
