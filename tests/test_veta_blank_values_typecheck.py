"""Every field's `blank_value` must be a shape its own declared type accepts.

WHY THIS FILE EXISTS. `blank_value` is what DID-matlab puts into a BLANK
document -- `did2.schema.cache.buildBlockFromEntries` (`cache.m:1588`) and its
nested twin `buildBlankStructure` (`:1617`) are the ONLY two consumers of the
key in `src/`. The same class then type-checks the field with
`validateTypeShape` (`cache.m:1764`). Nothing had ever compared the two, so a
schema could declare a blank the validator would reject -- a document built
from the schema failing its own schema.

Two fields did. `subjectmeasurement.datestamp` and
`absolute_reference.value.start.utc` are `timestamp`-typed and carried
`blank_value: 0.0`, while validateTypeShape accepts `timestamp` only as
char/scalar-string. `base.datestamp` was right (`''`) purely by accident of
provenance: it is copied verbatim from the V_zeta snapshot and never passes
through `build_v_eta.py`'s `field()`/`subfield()` blank ladders, which
special-cased `char`/`string` and let every other scalar type fall through to
`0.0`.

THIS TEST IS DELIBERATELY NOT ABOUT `timestamp`. Special-casing the one type
that bit us would leave the mechanism -- a blank ladder that does not know the
validator's type table -- fully intact for the next type. So it transcribes
validateTypeShape's whole switch and scans EVERY field of EVERY built schema,
nested fields included.

WHAT IT CANNOT DO. There is no MATLAB and no Octave in the container this was
written in (`command -v matlab; command -v octave; command -v octave-cli` --
all three exit 1), so nothing here has been run against the real validator.
This is a transcription of two code paths, and it can only be as right as the
transcription. `_ACCEPTS` names the file and line it came from so a reader can
check it rather than trust it.

WHAT IT DOES NOT CLAIM. A green run does NOT mean blank documents validate.
`blank_value` is one of several gates -- `mustBeNonEmpty`, `mustBeScalar`,
`constraints` and the vacuity rule all run too, and an unmodified blank
document fails on `base.session_id`'s emptyField long before any of them (see
DID-matlab `tests/+did2/+unittest/testEnforceNonVacuousFields.m:290`). This
file checks ONE property: type-shape agreement between a declared blank and its
declared type.

DENOMINATOR: every counting assertion states what it counted.
"""
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VETA = os.path.join(REPO_ROOT, "schemas", "V_eta")

# Not schemas: the build's index and topic manifests carry no `fields`.
NON_SCHEMA = {"index.json", "topics.json"}

# ---------------------------------------------------------------------------
# Transcription of DID-matlab src/did/+did2/+schema/cache.m:1764
# validateTypeShape. Each branch below names the MATLAB predicate it stands
# for. The MATLAB side sees the blank AFTER `jsondecode`, so the JSON->MATLAB
# mapping is part of the transcription:
#
#     JSON ""      -> char ''          ischar    -> true
#     JSON null    -> []               isnumeric -> true, ischar -> false
#     JSON []      -> 0x0 double       isnumeric -> true
#     JSON true    -> logical          islogical -> true, isnumeric -> FALSE
#     JSON 0.0     -> double           isnumeric -> true
#     JSON {}      -> struct, 0 fields isstruct  -> true
# ---------------------------------------------------------------------------

# case {'char', 'did_uid', 'timestamp'}: ischar || (isstring && isscalar)
CHAR_ONLY_TYPES = ("char", "did_uid", "timestamp")

# case {'duration','volume','mass','length','voltage','current','frequency',
#       'concentration','ontology_term'}: isstruct
NAMED_COMPOSITE_TYPES = ("duration", "volume", "mass", "length", "voltage",
                         "current", "frequency", "concentration", "ontology_term")


def _flatten(seq):
    for x in seq:
        if isinstance(x, list):
            yield from _flatten(x)
        else:
            yield x


def _numeric(v):
    # islogical is NOT isnumeric in MATLAB, and Python bool subclasses int.
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _accepts(ftype, blank):
    """True when validateTypeShape would let `blank` pass for `ftype`."""
    v = [] if blank is None else blank          # jsondecode(null) -> []

    if ftype in CHAR_ONLY_TYPES:
        return isinstance(v, str)

    if ftype == "string":
        # Wider case: char, string array, cell-of-chars, or empty numeric.
        if isinstance(v, str):
            return True
        return isinstance(v, list) and all(isinstance(x, str) for x in v)

    if ftype == "boolean":
        # islogical || (isnumeric && all(v(:) == 0 | v(:) == 1)).
        # `all` of an EMPTY array is true, so [] passes -- deliberately.
        if isinstance(v, bool):
            return True
        if _numeric(v):
            return v in (0, 1)
        return isinstance(v, list) and all(_numeric(x) and x in (0, 1) for x in _flatten(v))

    if ftype == "integer":
        # isnumeric && ~any(mod(v(:),1) ~= 0); `any` of empty is false, so []
        # passes. A logical is not isnumeric, so it does not.
        if _numeric(v):
            return float(v).is_integer()
        return isinstance(v, list) and all(_numeric(x) and float(x).is_integer()
                                           for x in _flatten(v))

    if ftype in ("double", "matrix"):
        return _numeric(v) or (isinstance(v, list)
                               and all(_numeric(x) for x in _flatten(v)))

    if ftype == "structure" or ftype in NAMED_COMPOSITE_TYPES:
        return isinstance(v, dict)

    # `otherwise`: unknown types are tolerated by the validator, so they are
    # tolerated here. The meta-schema's type enum is what gates new types.
    return True


def _structure_blank_is_rebuilt(ftype, blank):
    """cache.m:1589-1592 and :1618-1621.

    A `structure`-typed field whose declared blank is EMPTY never reaches
    validateTypeShape as that blank: both builders substitute
    `buildBlankStructure(fieldDef)`, a real struct assembled from the
    sub-field blanks. So `structure` + `[]` is benign BY CONSTRUCTION, and
    counting it as a defect would bury the real ones under 28 false rows.

    The substitution is keyed on `strcmp(fieldType,'structure')`, so it does
    NOT cover the named composite types -- their empty/numeric blanks land
    literally, which is why they appear in KNOWN_DIVERGENT below.
    """
    return ftype == "structure" and blank in (None, [], {})


# ---------------------------------------------------------------------------
# The rows that DIVERGE today. Pinned exactly, not as a threshold, so the set
# cannot grow silently AND cannot shrink silently: a repair has to say so here.
#
# NONE of these is a `timestamp`. They are two other families, both left alone
# on purpose -- this change fixes the type it was sent to fix and reports the
# rest rather than widening its own blast radius:
#
#   (1) 24 NAMED COMPOSITE fields blank as `0.0` or `[]` where the validator
#       wants a struct. This is the same defect class and it is REAL: 42 of the
#       66 named-composite fields in the built set already blank as a struct
#       (e.g. `session_bounded_reference.start`, a `duration`, blanks as
#       {approximate, source_unit, source_value}), so the struct blank is the
#       established convention and these 24 are the ones that missed it. Not
#       fixed here because choosing each type's blank struct is a modelling
#       call across ~15 classes, not a ladder fix.
#
#   (2) 3 `pyraview` `matrix` fields blank as `''`. These are NOT authored by
#       build_v_eta.py at all -- they are copied verbatim from
#       schemas/V_zeta/stable/pyraview.json by the copytree that starts the
#       build. Repairing them needs an explicit transform, which is a decision
#       about the V_zeta snapshot, not a bug in a helper.
#
# Each entry is (class_name, dotted field path, declared type).
# ---------------------------------------------------------------------------
KNOWN_DIVERGENT = {
    ("absolute_reference", "value.duration", "duration"),
    ("chemical", "value.amount", "concentration"),
    ("concentration", "value", "concentration"),
    ("current", "value", "current"),
    ("dose", "value.formulation.chemicals.amount", "concentration"),
    ("dose", "value.volume", "volume"),
    ("duration", "value", "duration"),
    ("formulation", "value.chemicals.amount", "concentration"),
    ("frequency", "value", "frequency"),
    ("frequency_filter", "passband.high", "frequency"),
    ("frequency_filter", "passband.low", "frequency"),
    ("frequency_filter", "stopband.high", "frequency"),
    ("frequency_filter", "stopband.low", "frequency"),
    ("length", "value", "length"),
    ("mass", "value", "mass"),
    ("pyraview", "decimation_levels", "matrix"),
    ("pyraview", "decimation_sampling_rates", "matrix"),
    ("pyraview", "decimation_start_times", "matrix"),
    ("relative_reference", "value.duration", "duration"),
    ("relative_reference", "value.start", "duration"),
    ("sampled_body", "sample_time.dt", "duration"),
    ("sampled_body", "sample_time.t0", "duration"),
    ("subject_interaction", "sample_time.dt", "duration"),
    ("subject_statement", "conditions.term.value", "ontology_term"),
    ("time_reference", "clock_tolerance", "duration"),
    ("voltage", "value", "voltage"),
    ("volume", "value", "volume"),
}


def _schema_files():
    out = []
    for tier in sorted(os.listdir(VETA)):
        d = os.path.join(VETA, tier)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".json") and name not in NON_SCHEMA:
                out.append(os.path.join(d, name))
    return out


def _scan():
    """Walk every field of every built schema. Returns (stats, divergent)."""
    stats = {"files": 0, "files_with_fields": 0, "fields": 0,
             "structure_blanks_rebuilt": 0, "by_type": {}}
    divergent = set()
    detail = {}

    def walk(fields, path, cls):
        for f in fields or []:
            stats["fields"] += 1
            here = path + [f.get("name", "<unnamed>")]
            ftype = f.get("type")
            blank = f.get("blank_value")
            stats["by_type"][ftype] = stats["by_type"].get(ftype, 0) + 1
            if not _accepts(ftype, blank):
                if _structure_blank_is_rebuilt(ftype, blank):
                    stats["structure_blanks_rebuilt"] += 1
                else:
                    key = (cls, ".".join(here), ftype)
                    divergent.add(key)
                    detail[key] = blank
            walk(f.get("fields"), here, cls)

    for path in _schema_files():
        stats["files"] += 1
        with open(path) as fh:
            doc = json.load(fh)
        if not isinstance(doc, dict) or "fields" not in doc:
            continue
        stats["files_with_fields"] += 1
        cls = (doc.get("document_class") or {}).get("class_name",
                                                    os.path.basename(path))
        walk(doc.get("fields"), [], cls)
    return stats, divergent, detail


def _denominator(stats):
    return (f"DENOMINATOR: {stats['files']} schema file(s) under schemas/V_eta/ "
            f"({stats['files_with_fields']} declaring `fields`), "
            f"{stats['fields']} field entr(ies) read INCLUDING nested, "
            f"{len(stats['by_type'])} distinct declared type(s); "
            f"{stats['structure_blanks_rebuilt']} structure blank(s) excluded as "
            f"rebuilt by buildBlankStructure")


def test_scan_actually_read_something():
    """Rule 5. A zero-denominator scan reports 'clean' and means 'blind'."""
    stats, _, _ = _scan()
    print(_denominator(stats))
    assert stats["files"] >= 200, _denominator(stats)
    assert stats["files_with_fields"] >= 200, _denominator(stats)
    assert stats["fields"] >= 900, _denominator(stats)
    # If the whole set ever became one type, the scan below would pass
    # vacuously; it is 38 types today.
    assert len(stats["by_type"]) >= 20, _denominator(stats)


def test_every_timestamp_blank_is_char():
    """The specific regression: a numeric blank on a char-only type.

    Stated per-type rather than per-field so a NEW `timestamp` field is
    covered the day it is added, and asserted on `default_value` too -- the
    ladders derive one from the other, so they went wrong together.
    """
    stats, _, _ = _scan()
    rows = []

    def walk(fields, path, cls):
        for f in fields or []:
            here = path + [f.get("name", "<unnamed>")]
            if f.get("type") in CHAR_ONLY_TYPES:
                rows.append((cls, ".".join(here), f.get("type"),
                             f.get("blank_value"), f.get("default_value")))
            walk(f.get("fields"), here, cls)

    for path in _schema_files():
        with open(path) as fh:
            doc = json.load(fh)
        if not isinstance(doc, dict) or "fields" not in doc:
            continue
        cls = (doc.get("document_class") or {}).get("class_name",
                                                    os.path.basename(path))
        walk(doc.get("fields"), [], cls)

    print(_denominator(stats))
    print(f"char-only-typed field(s) ({'/'.join(CHAR_ONLY_TYPES)}): {len(rows)}")
    for cls, p, t, b, d in sorted(rows):
        print(f"  {cls}.{p}  type={t}  blank={b!r}  default={d!r}")

    assert rows, "no char-only-typed fields found at all -- the scan is blind"
    assert any(t == "timestamp" for _, _, t, _, _ in rows), (
        "no `timestamp` field found; this test would pass vacuously")

    bad_blank = [(c, p, t, b) for c, p, t, b, _ in rows if not isinstance(b, str)]
    assert not bad_blank, (
        "blank_value must be a JSON string for a char-only type "
        "(cache.m:1764 accepts only ischar/isstring): " + repr(bad_blank))
    bad_default = [(c, p, t, d) for c, p, t, _, d in rows if not isinstance(d, str)]
    assert not bad_default, (
        "default_value must be a JSON string for a char-only type: "
        + repr(bad_default))


def test_blank_values_match_the_validators_accepted_shapes():
    """The general sweep, pinned both ways.

    A NEW divergence fails (the defect this file exists to catch). A repaired
    one ALSO fails, because a shrinking set that nobody notices is how a fixed
    thing gets re-broken quietly -- the fixer removes the row here and says so.
    """
    stats, divergent, detail = _scan()
    print(_denominator(stats))
    print(f"blank_value(s) validateTypeShape would REJECT: {len(divergent)} "
          f"(expected {len(KNOWN_DIVERGENT)}, all pre-existing and listed in "
          f"KNOWN_DIVERGENT)")
    for key in sorted(divergent):
        print(f"  {key[0]}.{key[1]}  type={key[2]}  blank={detail[key]!r}")

    new = divergent - KNOWN_DIVERGENT
    assert not new, (
        "NEW blank_value/type mismatch(es) -- a blank document would carry a "
        "value its own field type rejects (DID-matlab cache.m:1764): "
        + repr(sorted(new)))

    fixed = KNOWN_DIVERGENT - divergent
    assert not fixed, (
        "these rows are listed as divergent but no longer are; delete them "
        "from KNOWN_DIVERGENT in the same commit that repairs them: "
        + repr(sorted(fixed)))


def test_no_timestamp_row_is_parked_in_the_known_list():
    """Guards against the easy wrong fix.

    Adding the two `timestamp` rows to KNOWN_DIVERGENT would have made this
    file green while changing nothing -- an allow-list is only honest if the
    thing it must never contain is named.
    """
    parked = [r for r in KNOWN_DIVERGENT if r[2] in CHAR_ONLY_TYPES]
    print(f"DENOMINATOR: {len(KNOWN_DIVERGENT)} KNOWN_DIVERGENT row(s) inspected; "
          f"{len(parked)} of a char-only type")
    assert not parked, (
        "a char-only-typed field must be REPAIRED in build_v_eta.py's blank "
        "ladder, never parked in KNOWN_DIVERGENT: " + repr(parked))


def test_the_blank_ladder_knows_the_validators_char_only_types():
    """The generator's constant must cover the validator's char-only case.

    The fix is one shared tuple in build_v_eta.py rather than three literals in
    two ladders. This pins that it still contains every char-only type; if
    DID-matlab widens the case, this fails and points at the ladder.
    """
    src = os.path.join(REPO_ROOT, "tools", "build_v_eta.py")
    with open(src) as fh:
        text = fh.read()
    marker = "_CHARLIKE_BLANK_TYPES = ("
    assert marker in text, (
        f"{src} no longer defines _CHARLIKE_BLANK_TYPES; the blank ladders "
        "have gone back to inline literals, which is how `timestamp` was "
        "missed in the first place")
    decl = text.split(marker, 1)[1].split(")", 1)[0]
    missing = [t for t in CHAR_ONLY_TYPES if f'"{t}"' not in decl]
    print(f"DENOMINATOR: {len(CHAR_ONLY_TYPES)} char-only type(s) required by "
          f"cache.m:1764; declared tuple = ({decl.strip()})")
    assert not missing, (
        "_CHARLIKE_BLANK_TYPES omits type(s) the validator accepts only as "
        "char: " + repr(missing))
    # Both ladders must read the constant, not a literal of their own.
    assert text.count("ftype in _CHARLIKE_BLANK_TYPES") == 2, (
        "expected both the subfield() and field() blank ladders to consult "
        "_CHARLIKE_BLANK_TYPES")
