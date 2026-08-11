#!/usr/bin/env python3
"""Phase 0 of V_eta_ground_truth_plan.md -- extract the did_v1 GROUND TRUTH.

WHY THIS EXISTS
---------------
The migrators were written against DID-schema's own `V_alpha` snapshot instead of
the real NDI document templates. Where the snapshot was wrong, a migrator reads
fields the source document does not have and emits an EMPTY BUT VALID document:
an all-blank composite still has fieldnames so it passes `mustBeNonEmpty`, and an
empty depends_on edge is skipped by the reference validator. The corpus gate stays
green and the data quietly goes missing. `distance_metadata`, `ontology_image` and
`ontology_label` are confirmed instances.

So this tool makes the real thing machine-readable, and every later phase checks
against it rather than against anything on the DID side.

WHAT IT EMITS  (schemas/V_eta_ndi_ground_truth.json)
----------------------------------------------------
  classes[<ndi class name>]:
      fields            declared property-block field names (snake-cased)
      raw_fields        as spelled in the template
      depends_on        dependency names (TEMPLATE u SCHEMA DOC -- see below)
      depends_on_template  dependency names the TEMPLATE declares
      depends_on_schema    dependency names the SCHEMA DOCUMENT declares
      depends_on_required  {name: true|false} -- `mustbenotempty` AS STATED BY
                        NDI. A name absent from this map is a name NDI states
                        nothing about; that is NOT the same as `false`, and the
                        two are kept apart on purpose.
      schema_document_form  'flat' | 'json_schema' | 'absent' -- WHICH NDI FILE
                        COULD HAVE SAID. `json_schema` and `absent` mean the
                        required-ness question was never answerable for this
                        class, not that the answer was no.
      files             declared file names
      superclasses      referenced superclass template basenames
      path              template path @ ref

  WHERE REQUIRED-NESS LIVES, AND WHY BOTH NDI FILES ARE RECORDED
  --------------------------------------------------------------
  The ground-truth rule is "where template and WRITER disagree, the writer
  wins". That rule does not arbitrate here: the TEMPLATE and the SCHEMA
  DOCUMENT are both NDI's own files, neither is a writer, and they say
  DIFFERENT KINDS OF THING. The template's `depends_on` entry is
  `{name, value:""}` -- a slot, with no required-ness at all. The flat schema
  document's is `{name, mustbenotempty: 0|1}` -- the assertion. Measured, not
  assumed:

      $ git grep -il "mustbenotempty" origin/main -- 'database_documents/*' | wc -l
      0
      $ git grep -il "mustbenotempty" origin/main -- 'schema_documents/*' | wc -l
      59

  So this tool records each side SEPARATELY (`depends_on_template` /
  `depends_on_schema` / `depends_on_required`) and prefers neither. The
  summary states how many classes could not answer at all, because a class
  whose schema document is in the JSON Schema form states no required-ness
  anywhere -- and a consumer that reads a missing `mustbenotempty` as `false`
  would turn "NDI never said" into "NDI said optional".
  v_alpha_divergence[]  classes whose V_alpha snapshot disagrees with the template
  migrator_reads[]      J migrators reading names no template has  (the suspects)
  writer_divergence[]   hand-recorded: shipped writer emits what the template does not
  writer_dependencies[] #54: dependency names a WRITER sets that NO template declares.
                        The one direction no checker could see -- the tombstone
                        checker compares a V_eta class against the TEMPLATE, and
                        the template does not have these either.

The NDI templates are read from `origin/main` via git, NOT the working tree --
same rule as tools/coverage.py, because a V_eta feature branch of NDI can lag main.
THAT RULE BINDS THE PROVENANCE WALK TOO: `classify_divergence` walks the SAME ref
this file records as `ndi_ref` and no other, so the artifact is reproducible from
NDI `origin/main` alone. It said `--all` until 2026-08-11, and 12 of the 67
provenance rows were being read off refs that are not ancestors of origin/main.

Usage:  python3 tools/ndi_ground_truth.py [--ndi /path/to/NDI-matlab]
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "schemas", "V_eta_ndi_ground_truth.json")
DDIR = "src/ndi/ndi_common/database_documents"
SDIR = "src/ndi/ndi_common/schema_documents"
# Filled by _schema_deps; reported in the ground-truth summary.
SCHEMA_SCAN = {"files": 0, "flat_form": 0, "json_schema_form": 0, "unparseable": 0}
# Filled by _merge_schema_deps; reported in the ground-truth summary. This is
# the denominator for the "NDI requires it, V_eta does not" census downstream:
# every zero it can print has to be distinguishable from "the question was
# never answerable for this class".
REQUIRED_SCAN = {
    "ndi_classes": 0,
    "classes_with_flat_schema_document": 0,
    "classes_with_json_schema_document": 0,
    "classes_with_no_schema_document": 0,
    "templates_carrying_mustbenotempty": 0,
    "dependency_names_total": 0,
    "dependency_names_with_a_required_statement": 0,
    "dependency_names_required": 0,
    "dependency_names_optional": 0,
    "dependency_names_ndi_states_nothing_about": 0,
}

# Divergences between a shipped NDI template and the writer that actually produces
# the documents. The DATA FOLLOWS THE WRITER, so the writer wins for migration --
# and each entry here is worth reporting upstream to NDI. Hand-maintained: found by
# reading the writer, which no static scan of the templates can do for us.
WRITER_DIVERGENCE = [
    {
        "class": "ontologyImage",
        "template_says": "ontologyNode (singular, a single CURIE)",
        "writer_emits": "ontologyNodes (plural) -- a comma-joined, sorted list of "
                        "ONE OR MORE CURIEs, each normalised via ndi.ontology.lookup",
        "writer": "NDI-matlab +ndi/+setup/+NDIMaker/imageDocMaker.m:80-85,122",
        "note": "The writer's own lookup query also uses the plural "
                "(ndi.query('ontologyImage.ontologyNodes', ...)), so the plural is "
                "authoritative and the template is stale. Multi-CURIE means a single "
                "ontology_term field cannot hold it.",
    },
    {
        "class": "hartley_reverse_correlation",
        "template_says": "hartley_numbers: [] (an empty matrix)",
        "writer_emits": "a struct {S, KXV, KYV, ORDER} of parallel per-frame arrays",
        "writer": "NDIcalc-vis-matlab +ndi/+calc/+vis/hartley.m:405-408",
        "note": "The V_delta conversion doc recorded it as matrix<double>, matching "
                "the template rather than the data.",
    },
    {
        "class": "ngrid",
        "template_says": "coordinates (declared, and genuinely populated)",
        "writer_emits": "coordinates -- concatenated per-axis coordinates, "
                        "size [sum(data_dim), 1]",
        "writer": "NDIcalc-vis hartley.m:443-445; NDI ndi.fun.data.mat2ngrid",
        "note": "NOT a template/writer disagreement -- recorded because the MIGRATOR "
                "(+did2/+convert/+migrators/ngrid.m) deletes it with rmfield, so real "
                "coordinate data is dropped today. Phase 3.",
    },
]


def snake(n):
    """EXACT port of universalRenames.m's snakeCase -- acronym-aware.

    The previous one-liner inserted `_` before every uppercase letter, which is
    NOT what the migration pipeline does and produced field names no document
    ever has: `curated_output_MD5_checksum` came out `curated_output_m_d5_checksum`
    and `integerIDs_A` came out `integer_i_ds_a`. Any comparison against those is
    a false positive, and the whole point of this file is to be the thing that is
    trusted, so it has to match the real transform character for character.

    A run of two or more uppercase letters is one acronym: lowercased with no
    internal separator ('MD5' -> 'md5', 'XMLParser' -> 'xml_parser'). A separator
    goes in before an uppercase letter when the previous character is NOT
    uppercase (the classic camelCase boundary), or when the previous IS uppercase
    and the next is lowercase (acronym-to-word). Never doubled after an existing
    underscore."""
    n = str(n)
    if not n:
        return n
    out = n[0].lower()
    for k in range(1, len(n)):
        c = n[k]
        if not c.isupper():
            out += c
            continue
        prev_upper = n[k - 1].isupper()
        next_lower = k + 1 < len(n) and n[k + 1].islower()
        if (not prev_upper or next_lower) and out[-1] != "_":
            out += "_" + c.lower()
        else:
            out += c.lower()
    return out


def _load_ndi_json(blob):
    """Parse an NDI JSON file, tolerating the MATLAB-isms in two of them.

    `apps/markgarbage/valid_interval_schema.json` and
    `apps/calculations/simple_calc_schema.json` contain `"parameters":
    [-Inf,Inf,0]`. `-Inf` is not JSON, so a strict parse throws and BOTH FILES
    BECOME INVISIBLE -- including their perfectly well-formed `depends_on`
    blocks, which sit above the offending line. `valid_interval` is one of the
    four UNVERIFIED coverage rows, so its declaration going unread was not free.

    Retried with the bare tokens replaced by null. That loses the parameter
    bounds and keeps everything else, which is the right trade for a sweep that
    only reads dependency names.
    """
    try:
        return json.loads(blob)
    except Exception:
        pass
    patched = re.sub(r"(?<![\"\w.])-?(?:Inf|NaN)(?![\"\w])", "null", blob)
    try:
        return json.loads(patched)
    except Exception:
        return None


def _json_schema_deps(d):
    """(classname, [dependency names]) from a JSON Schema-shaped NDI schema doc."""
    if "$schema" not in d and "properties" not in d:
        return None, []
    title = d.get("title") or ""
    cn = title.split("_")[-1] if title else ""
    # the title is `ndi_document_apps_<app>_<class>`; fall back to the id path
    ident = d.get("id") or ""
    if ident:
        base = os.path.basename(ident).replace(".json", "")
        if base:
            cn = base
    items = (((d.get("properties") or {}).get("depends_on") or {}).get("items")) or []
    if isinstance(items, dict):
        items = [items]
    names = []
    for it in items:
        if not isinstance(it, dict):
            continue
        const = (((it.get("properties") or {}).get("name") or {}).get("const"))
        if const:
            names.append(const)
    return cn, names


def _schema_deps(ndi_path, ref):
    """{class_name: {names, required, form}} from NDI's SCHEMA documents.

    `names`    dependency names the schema document declares
    `required` {name: bool} from `mustbenotempty`. A name is IN this map only
               when the schema document actually carried the key -- absence is
               "NDI states nothing", never `false`.
    `form`     'flat' or 'json_schema'. The JSON Schema form has no
               `mustbenotempty` anywhere (checked: 0 of the 5 files carry it),
               so for those five classes required-ness is UNSTATED. Reading
               that as optional would manufacture agreement with V_eta out of
               NDI's silence -- the absence-of-evidence error this repository
               keeps making, one field along.

    A DEPENDENCY CAN BE DECLARED IN THE SCHEMA AND NOT IN THE TEMPLATE, and
    reading only the template then reports the real edge as a DID-side invention.
    Live case: `daq/syncgraph.json` has `depends_on: []` while
    `schema_documents/daq/syncgraph_schema.json` declares
    `{"name": "syncrule_id", "mustbenotempty": 0}` -- and the writer sets it,
    `+ndi/+time/syncgraph.m:850`. V_eta declared it correctly and was told off
    for it by check_tombstones on every run.

    The two sides are UNIONED, never intersected: each is a place NDI states a
    dependency, and a name appearing in either is real.
    """
    out = {}
    # Which classes had a READABLE schema document at all, and in which form --
    # tracked separately from `out`, which only carries classes that declare a
    # dependency. Without this, a class whose schema document declares no
    # dependency and a class with no schema document at all are the same empty
    # record, and the required-ness census cannot tell "nothing is required"
    # from "nothing was read".
    forms = {}
    # DENOMINATOR, tracked in the module so the caller can report it. Reading a
    # schema-document set and finding nothing must never look like finding
    # nothing to find.
    stats = SCHEMA_SCAN
    stats.update({"files": 0, "flat_form": 0, "json_schema_form": 0, "unparseable": 0})
    if ref == "worktree":
        root = os.path.join(ndi_path, SDIR)
        paths = []
        for dirpath, _, names in os.walk(root):
            paths += [os.path.join(dirpath, n) for n in names if n.endswith(".json")]
        blobs = []
        for p in paths:
            try:
                blobs.append(open(p).read())
            except Exception:
                continue
    else:
        try:
            files = subprocess.run(
                ["git", "-C", ndi_path, "ls-tree", "-r", "--name-only", ref, "--", SDIR],
                capture_output=True, text=True, check=True).stdout.splitlines()
        except Exception:
            return out, forms
        blobs = []
        for f in files:
            if not f.endswith(".json"):
                continue
            try:
                blobs.append(subprocess.run(
                    ["git", "-C", ndi_path, "show", "%s:%s" % (ref, f)],
                    capture_output=True, text=True, check=True).stdout)
            except Exception:
                continue
    stats["files"] = len(blobs)
    for blob in blobs:
        d = _load_ndi_json(blob)
        if d is None:
            stats["unparseable"] += 1
            continue
        # A SECOND SCHEMA FORMAT. Five of NDI's 89 schema documents -- the whole
        # `vhlab_voltage2firingrate` family -- are JSON Schema draft 2019-09
        # instead of the flat shape, with the dependency names as `const` values
        # nested under properties.depends_on.items[]. Reading only the flat shape
        # skipped them silently, so `binnedspikeratevm.sorting_parameters_id` read
        # as a DID-side invention when NDI's own schema declares it.
        #
        # This family matters more than its size: its WRITER is in no repository
        # we have, so this schema is the ONLY ground truth available for it.
        js_cn, js_deps = _json_schema_deps(d)
        if js_cn and js_deps:
            stats["json_schema_form"] += 1
            rec = out.setdefault(js_cn, {"names": [], "required": {},
                                         "form": "json_schema"})
            rec["form"] = "json_schema"
            rec["names"].extend(js_deps)
            forms[js_cn] = "json_schema"
            continue
        if js_cn:
            # A JSON Schema-form document that declares no dependency at all.
            # It still PROVES the class was read, which is the difference
            # between "no required edges" and "no file to read".
            forms.setdefault(js_cn, "json_schema")
        # THE KEY IS `classname`. Schema documents do not use the template's
        # `document_class.class_name` shape -- they are flat, with `classname`.
        # A first cut read the template spelling, matched nothing, and returned a
        # clean empty result: exactly the "a grep that could not have matched"
        # failure, caught here only because a row that should have disappeared
        # did not.
        dc = d.get("document_class") or {}
        cn = d.get("classname") or dc.get("class_name") or d.get("class_name")
        deps = d.get("depends_on") or []
        if isinstance(deps, dict):
            deps = [deps]
        names = [x.get("name") for x in deps
                 if isinstance(x, dict) and x.get("name")]
        if cn:
            forms.setdefault(cn, "flat")
        if cn and names:
            stats["flat_form"] += 1
            rec = out.setdefault(cn, {"names": [], "required": {},
                                      "form": "flat"})
            rec["form"] = "flat"
            rec["names"].extend(names)
            for x in deps:
                if not isinstance(x, dict) or not x.get("name"):
                    continue
                # THE KEY IS OPTIONAL AND ITS ABSENCE IS NOT `false`. Record a
                # verdict only when NDI wrote one. `mustbenotempty` is NDI's
                # spelling -- all lowercase, no camelCase -- and getting that
                # wrong would return an all-absent map that reads exactly like
                # "NDI requires nothing", which is the reassuring direction.
                if "mustbenotempty" in x:
                    rec["required"][x["name"]] = bool(x["mustbenotempty"])
    return out, forms


def _merge_schema_deps(out, ndi_path, ref):
    """Union the schema documents' dependency names into the template records,
    and record WHAT EACH NDI FILE SAID separately.

    The union of NAMES is unchanged -- each side is a place NDI declares an
    edge, so a name in either is real. What is NEW is that the two sides stop
    being indistinguishable afterwards: `depends_on_template` and
    `depends_on_schema` say which file carried each name, and
    `depends_on_required` carries the schema document's `mustbenotempty`
    verdicts and ONLY those.

    Every counter below is filled for EVERY class, including the classes with
    no schema document at all -- a class that could not be asked has to be
    countable, or the downstream census reports "NDI requires nothing here"
    for a class nobody ever read.
    """
    extra, forms = _schema_deps(ndi_path, ref)
    scan = REQUIRED_SCAN
    scan.update({k: 0 for k in scan})
    scan["ndi_classes"] = len(out)
    for cn, rec in out.items():
        tmpl = list(rec["depends_on"])
        rec["depends_on_template"] = tmpl
        # The TEMPLATE never states required-ness. That is measured, not
        # assumed: _parse reads the raw dependency objects and this counter
        # would be non-zero if one ever grew the key.
        scan["templates_carrying_mustbenotempty"] += rec.pop(
            "_template_mustbenotempty", 0)
        # THE FORM COMES FROM `forms`, NOT FROM `extra`. `extra` only holds
        # classes that declare a dependency, so reading the form off it made
        # every class with a schema document and no dependency indistinguishable
        # from a class with no schema document at all -- 29 classes reported as
        # "never asked" when all 29 had been read and had answered "no edges".
        # That is precisely the zero this block exists to disambiguate, and the
        # first cut of it got the disambiguation backwards.
        sub = extra.get(cn)
        form = forms.get(cn, "absent")
        rec["schema_document_form"] = form
        if form == "flat":
            scan["classes_with_flat_schema_document"] += 1
        elif form == "json_schema":
            scan["classes_with_json_schema_document"] += 1
        else:
            scan["classes_with_no_schema_document"] += 1
        if sub is None:
            rec["depends_on_schema"] = []
            rec["depends_on_required"] = {}
        else:
            rec["depends_on_schema"] = sorted(set(sub["names"]))
            rec["depends_on_required"] = dict(sorted(sub["required"].items()))
            have = set(tmpl)
            rec["depends_on"] = tmpl + sorted(
                n for n in set(sub["names"]) if n not in have)
        for n in rec["depends_on"]:
            scan["dependency_names_total"] += 1
            if n in rec["depends_on_required"]:
                scan["dependency_names_with_a_required_statement"] += 1
                if rec["depends_on_required"][n]:
                    scan["dependency_names_required"] += 1
                else:
                    scan["dependency_names_optional"] += 1
            else:
                scan["dependency_names_ndi_states_nothing_about"] += 1
    return out


def ndi_templates(ndi_path):
    """Read every NDI document template from origin/main (falling back to main,
    then the working tree). Returns (dict, ref)."""
    for ref in ("origin/main", "main"):
        try:
            files = subprocess.run(
                ["git", "-C", ndi_path, "ls-tree", "-r", "--name-only", ref, "--", DDIR],
                capture_output=True, text=True, check=True).stdout.splitlines()
        except Exception:
            continue
        out = {}
        for f in files:
            if not f.endswith(".json"):
                continue
            try:
                blob = subprocess.run(["git", "-C", ndi_path, "show", "%s:%s" % (ref, f)],
                                      capture_output=True, text=True, check=True).stdout
                d = json.loads(blob)
            except Exception:
                continue
            rec = _parse(d, "%s @%s" % (f, ref))
            if rec:
                out[rec.pop("_class")] = rec
        if out:
            return _merge_schema_deps(out, ndi_path, ref), ref
    # working-tree fallback
    out = {}
    root = os.path.join(ndi_path, DDIR)
    for dirpath, _, names in os.walk(root):
        for n in names:
            if not n.endswith(".json"):
                continue
            p = os.path.join(dirpath, n)
            try:
                d = json.load(open(p))
            except Exception:
                continue
            rec = _parse(d, os.path.relpath(p, ndi_path) + " @worktree")
            if rec:
                out[rec.pop("_class")] = rec
    return _merge_schema_deps(out, ndi_path, "worktree"), "worktree"


def writer_dependencies(ndi_path, truth):
    """Dependencies NDI's WRITERS set that no template declares.

    #54. Both existing checkers compare a V_eta tombstone against an NDI
    TEMPLATE, so they are blind in one direction: `set_dependency_value` and
    `add_dependency_value_n` accept `'ErrorIfNotFound', 0`, and in that mode
    `did/document.m:262-266` APPENDS an entry that no schema declares. The
    document then carries an edge that appears in no template and in no V_eta
    class, and `did2/+schema/cache.m:598` allows `depends_on` wholesale without
    checking individual names -- so nothing anywhere can see it.

    The live case is the openMINDS pedigree: `openMINDSobj2ndi_document.m:80-92`
    adds `openminds_1 .. openminds_n` for each `ndi://` child reference, and a
    bare `openminds` for a leaf. Those edges carry a Strain's backgroundStrain
    graph, and no template mentions them.

    This is a TEXTUAL sweep of NDI's .m files, so it reports call sites and not
    a proven per-class mapping: a writer may set an edge on a document whose
    class the call site does not name. Treat a row as a place to go and read,
    exactly as the tombstone checker's rows are treated.
    """
    # THE FIRST ARGUMENT IS OPTIONAL, and getting that wrong made this sweep
    # nearly blind. NDI writes these as METHOD calls -- `doc.set_dependency_value(
    # 'element_id', id)` -- where the dependency name is the FIRST argument. The
    # original pattern required `(<something>, 'name')`, i.e. the functional form
    # `set_dependency_value(doc, 'name', id)`, so it matched 5 call sites in 1,002
    # files and missed every method call, including all five in
    # +ndi/+app/+stimulus/tuning_response.m:323-328 and all three in
    # +ndi/+daq/system.m:489-497.
    #
    # It reported "0 dependencies declared by no template" and that read as a
    # clean bill of health. It was a property of the regex. The denominator added
    # below is what exposed it -- 5 call sites across a thousand files is not a
    # believable number, and nothing before printed the denominator to compare
    # against.
    pat = re.compile(
        r"(?:set_dependency_value|add_dependency_value_n)\s*\(\s*"
        r"(?:[^,'\")]+,\s*)?"
        r"['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]")
    declared = set()
    for rec in truth.values():
        declared.update(rec.get("depends_on") or [])
    hits = {}
    # DENOMINATOR. This sweep can now legitimately come back EMPTY -- once the
    # ground truth reads NDI's schema documents as well as its templates, every
    # writer-set dependency turns out to be declared somewhere. An empty list is
    # the right answer AND is indistinguishable from a scan that matched nothing
    # because its regex or its ref was wrong, which is the silentLoss failure
    # exactly. So the scan states what it looked at, unconditionally.
    scanned = {"files": 0, "call_sites": 0, "dependencies_seen": set()}
    for ref in ("origin/main", "main"):
        try:
            files = subprocess.run(
                ["git", "-C", ndi_path, "ls-tree", "-r", "--name-only", ref],
                capture_output=True, text=True, check=True).stdout.splitlines()
        except Exception:
            continue
        for f in files:
            if not f.endswith(".m"):
                continue
            try:
                blob = subprocess.run(["git", "-C", ndi_path, "show", "%s:%s" % (ref, f)],
                                      capture_output=True, text=True, check=True).stdout
            except Exception:
                continue
            # MATLAB continues a call across lines with `...`, and the live
            # case does exactly that (openMINDSobj2ndi_document.m:82-84), so a
            # line-at-a-time scan sees the call but not its dependency name.
            # Join continuations first, keeping the FIRST line's number.
            joined, lines = [], blob.splitlines()
            k = 0
            while k < len(lines):
                start, text = k + 1, lines[k].rstrip()
                while text.endswith("...") and k + 1 < len(lines):
                    k += 1
                    text = text[:-3] + lines[k].strip()
                joined.append((start, text))
                k += 1
            scanned["files"] += 1
            for i, line in joined:
                m = pat.search(line)
                if not m:
                    continue
                name = m.group(1)
                scanned["call_sites"] += 1
                scanned["dependencies_seen"].add(name)
                # `add_dependency_value_n('x', ...)` writes x_1, x_2, ...; a
                # template declaring `x_1` counts as declaring the family.
                if name in declared or any(d.startswith(name + "_") for d in declared):
                    continue
                hits.setdefault(name, []).append("%s:%d" % (f, i))
        if hits or files:
            break
    return ([{"dependency": k, "declared_by_no_template": True, "writer_sites": v}
             for k, v in sorted(hits.items())],
            {"m_files_scanned": scanned["files"],
             "dependency_call_sites": scanned["call_sites"],
             "distinct_dependencies_written": sorted(scanned["dependencies_seen"])})


def _parse(d, path):
    dc = d.get("document_class") or {}
    cn = dc.get("class_name")
    if not cn:
        return None
    blk = d.get(dc.get("property_list_name") or cn)
    raw = sorted(blk.keys()) if isinstance(blk, dict) else []
    deps = d.get("depends_on") or []
    if isinstance(deps, dict):
        deps = [deps]
    files = ((d.get("files") or {}).get("file_list")) or []
    if isinstance(files, str):
        files = [files]
    supers = []
    for s in dc.get("superclasses") or []:
        defn = s.get("definition", "")
        supers.append(os.path.basename(defn).replace(".json", ""))
    return {
        "_class": cn,
        "fields": sorted({snake(k) for k in raw}),
        "raw_fields": raw,
        "depends_on": [x.get("name") for x in deps if isinstance(x, dict) and x.get("name")],
        # Popped by _merge_schema_deps into REQUIRED_SCAN. Carried as data
        # rather than assumed to be zero: the claim "the template never states
        # required-ness" is the reason this whole extract reads the schema
        # documents at all, so it is measured on every run instead of being
        # written down once and quoted forward.
        "_template_mustbenotempty": sum(
            1 for x in deps
            if isinstance(x, dict) and "mustbenotempty" in x),
        "files": list(files),
        "superclasses": supers,
        "path": path,
    }


def v_alpha_divergence(truth):
    """Classes whose V_alpha snapshot disagrees with the real template. V_alpha is
    NOT authoritative -- this list exists to size the damage, not to arbitrate."""
    rows = []
    adir = os.path.join(REPO, "schemas", "V_alpha")
    if not os.path.isdir(adir):
        return rows
    by_snake = {snake(k): k for k in truth}
    for n in sorted(os.listdir(adir)):
        if not n.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(adir, n)))
        except Exception:
            continue
        cn = d.get("_classname") or n[:-5]
        key = by_snake.get(snake(cn))
        if not key:
            continue
        ours = {snake(f["_name"]) for f in d.get("_fields", []) if f.get("_name")}
        theirs = set(truth[key]["fields"])
        if ours != theirs:
            rows.append({
                "class": cn,
                "ndi_class": key,
                "only_in_our_snapshot": sorted(ours - theirs),
                "only_in_ndi_template": sorted(theirs - ours),
            })
    return rows


def migrator_reads(truth, did_path):
    """J migrators referencing field names that no NDI template has. Regex over the
    migrator source, so these are RANKED SUSPECTS, not confirmed bugs -- a name can
    appear in a comment. Confirm each against the template + writer before fixing."""
    rows = []
    mdir = os.path.join(did_path, "src/did/+did2/+convert/+migrators_j")
    if not os.path.isdir(mdir):
        return rows
    by_snake = {snake(k): k for k in truth}
    for n in sorted(os.listdir(mdir)):
        if not n.endswith(".m"):
            continue
        cls = n[:-2]
        key = by_snake.get(snake(cls))
        if not key:
            continue
        src = open(os.path.join(mdir, n), errors="replace").read()
        # Strip MATLAB comments and superclass/mixin cell literals before matching.
        # Both produced false positives on the first pass: `image_stack` was flagged
        # for `image_format` occurring only in a comment, and `treatment_drug` for
        # `{'dose'}` -- which is a V_eta data_type mixin passed to jStartInteraction,
        # not a did_v1 field read at all.
        src = "\n".join(re.sub(r"(?<!\.)%.*$", "", ln) for ln in src.splitlines())
        src = re.sub(r"\{\s*'[a-z0-9_']*(?:'\s*,\s*'[a-z0-9_]*)*'\s*\}", " ", src)
        theirs = set(truth[key]["fields"])
        alpha_only = _alpha_names(key) - theirs

        # TIER 1 (confident): the name appears in an idiom that can only be a READ
        # OF THE SOURCE BLOCK, and is a field our V_alpha snapshot claims but no NDI
        # template has -- i.e. the migrator provably took its vocabulary from the
        # snapshot. Deliberately NOT matching bare `x.field`: that cannot distinguish
        # reading the source from WRITING the emitted body, and it produced a false
        # positive on treatment_drug (`dose` is the V_eta output mixin, not a v1
        # field). Precision matters more than recall here -- tier 2 is the safety net.
        read = set(re.findall(r"(?:isfield|isstruct)\(\s*\w+\s*,\s*'([a-z0-9_]+)'", src))
        read |= set(re.findall(r"jGet\w*\(\s*\w+\s*,\s*'([a-z0-9_]+)'", src))

        # TIER 1b: the same idiom, but through a LOCAL accessor helper. Several
        # migrators define their own `getField(block, name)` / `numScalar(...)`
        # wrappers, and reads through those were invisible to the two patterns
        # above -- which is how vmspikesummary sat in tier 2 (see below) while
        # reading four names that do not exist. Any local function whose body
        # calls isfield or uses dynamic field access is treated as an accessor.
        local_fns = re.findall(r"^\s*function\s+(?:[\[\]\w,\s~]+=\s*)?(\w+)\s*\(",
                               src, re.MULTILINE)
        accessors = set()
        for fn in local_fns:
            body = re.search(r"^\s*function\s+(?:[\[\]\w,\s~]+=\s*)?"
                             + re.escape(fn) + r"\s*\(.*?(?=^\s*function\s|\Z)",
                             src, re.MULTILINE | re.DOTALL)
            if body and re.search(r"isfield\s*\(|\.\(\s*\w+\s*\)", body.group(0)):
                accessors.add(fn)
        for fn in accessors:
            read |= set(re.findall(re.escape(fn) + r"\(\s*\w+\s*,\s*'([a-z0-9_]+)'",
                                   src))

        # TIER 1c: the accessor is called with a name we CANNOT resolve statically
        # -- a cell-table lookup like getField(blk, spec{k, 1}), which is exactly
        # what vmspikesummary does. The field names then live in a literal table
        # that no call-site pattern can follow. When that happens, every quoted
        # candidate name in the file is treated as read: we can no longer prove
        # which ones flow in, and under-reporting here is what let a whole class
        # be modelled against fields that do not exist.
        dynamic = any(re.search(re.escape(fn) + r"\(\s*\w+\s*,\s*\w+\s*[\{\(]", src)
                      for fn in accessors)
        if dynamic:
            read |= set(re.findall(r"'([a-z0-9_]+)'", src))

        tier1 = sorted(r for r in read if r in alpha_only)

        # TIER 2 (possible): the name occurs anywhere in the source. Catches reads
        # via helpers or dynamic field access that tier 1's idioms miss, at the cost
        # of matching comments. Confirm each against the template + writer.
        tier2 = sorted(f for f in alpha_only
                       if f not in tier1 and re.search(r"\b" + re.escape(f) + r"\b", src))

        if tier1 or tier2:
            rows.append({
                "migrator": n,
                "ndi_class": key,
                "confidence": "confirmed-vocabulary" if tier1 else "possible",
                "reads_names_absent_from_template": tier1,
                "mentions_names_absent_from_template": tier2,
                "template_fields": sorted(theirs),
            })
    return rows


def classify_divergence(ndi_path, ref, truth, div):
    """0.3 -- for each divergent class, was this NDI CHANGING its template (real
    drift, so old-shaped documents may exist and the migrator needs two paths), or
    did we INVENT the shape (only one shape ever existed, one path)?

    Decisive test: compare our V_alpha field set against the EARLIEST version of the
    NDI template. If they never matched, the snapshot was never a copy of NDI.

    UNKNOWN is honest, not benign: usually the earliest template predates the modern
    property-block format, so the comparison is not meaningful that far back. Those
    classes need reading by hand.

    THE WALK IS CONFINED TO `ref` -- THE SAME REF THE ARTIFACT DECLARES AS
    `ndi_ref`, AND NOTHING ELSE. It used to say `--all`, which made the answer a
    property of whichever refs the local NDI clone happened to carry rather than
    of NDI: the artifact recorded `ndi_ref: "origin/main"` and this file's own
    docstring said it never reads a feature branch, while 12 of the 67
    provenance rows were in fact read off refs that are not ancestors of
    origin/main (`treatment_drug` from `origin/feature/newvhlabimport`, `app` /
    `element` / `projectvar` from `origin/audri_documents`). A verdict derived
    from a ref the contract excludes is not evidence, so those rows were not
    "lost" when this changed -- they were withdrawn.

    `--no-renames` IS LOAD-BEARING, and dropping `--all` without it would have
    replaced one wrong answer with another. Rename detection is on by default,
    and a rename is reported as `R`, which `--diff-filter=A` then skips -- so a
    class whose template was ever renamed has no add-commit at all. Both kinds
    happened here: the basename changed
    (`ndi_document_stimulus_presentation.json` -> `stimulus_presentation.json`)
    and later the whole tree moved (fe64a9f53, "Move +ndi/ndi_common/java to
    src/ndi/", R100). MEASURED on origin/main, 67 divergent classes:

        origin/main                    333 basenames, 14 classes with NO add-commit
        origin/main --no-renames       374 basenames,  0 classes with NO add-commit

    `--full-history` changes NO verdict today -- measured, 0 of 67 -- and is
    kept only so the walk does not depend on which parent git's default
    simplification happens to follow through a merge (it recovers 2 further
    basenames overall: 374 -> 376). It is not what fixed the 14.

    With the ref pinned and renames off, every one of the 67 divergent classes
    resolves to a real first version on origin/main: `no add-commit found` is 0,
    and each UNKNOWN that remains is the honest kind -- a first version that
    predates the property-block format, or one that is not valid JSON.

    `%H` (full sha), not `%h`: abbreviation length is a function of how many
    objects the clone has, which is exactly the kind of clone-dependence this
    function is being repaired for."""
    def sh(*a):
        return subprocess.run(["git", "-C", ndi_path] + list(a),
                              capture_output=True, text=True).stdout

    first = {}
    cur = None
    # `ndi_templates` returns "worktree" when no git ref could be read at all.
    # There is then no ref to walk, and walking HEAD instead would be the same
    # substitution `--all` was making. Say so per row rather than guess.
    if ref != "worktree":
        for line in sh("log", ref, "--full-history", "--no-renames", "--reverse",
                       "--diff-filter=A", "--format=@%H %ai", "--name-only",
                       "--", "*.json").splitlines():
            if line.startswith("@"):
                cur = line[1:]
            elif line.endswith(".json") and cur:
                first.setdefault(line.rsplit("/", 1)[-1][:-5], (cur, line))

    out = {}
    for cn, rec in div.items():
        alpha = set(rec["only_in_our_snapshot"]) | (
            set(truth[cn]["fields"]) - set(rec["only_in_ndi_template"]))
        hit = first.get(cn)
        if not hit:
            out[cn] = {"verdict": "UNKNOWN",
                       "why": ("no ref to walk (ndi_ref=worktree)"
                               if ref == "worktree" else "no add-commit found")}
            continue
        sha, when = hit[0].split()[0], hit[0].split()[1]
        try:
            d = json.loads(sh("show", "%s:%s" % (sha, hit[1])))
            dc = d.get("document_class") or {}
            blk = d.get(dc.get("property_list_name") or dc.get("class_name"))
            if not isinstance(blk, dict):
                out[cn] = {"verdict": "UNKNOWN",
                           "why": "no property block at first version (%s)" % when}
                continue
            ff = {snake(k) for k in blk}
        except Exception:
            out[cn] = {"verdict": "UNKNOWN", "why": "unparseable first version"}
            continue
        out[cn] = {
            "verdict": "NDI-CHANGED" if ff == alpha else "DID-INVENTED",
            "why": "first NDI version %s" % when,
            "first_version_fields": sorted(ff),
        }
    return out


_ALPHA_CACHE = {}


def _alpha_names(ndi_class):
    """Field names our V_alpha snapshot claims for this class -- the vocabulary a
    migrator would have picked up if it was written from the snapshot."""
    if not _ALPHA_CACHE:
        adir = os.path.join(REPO, "schemas", "V_alpha")
        if os.path.isdir(adir):
            for n in os.listdir(adir):
                if not n.endswith(".json"):
                    continue
                try:
                    d = json.load(open(os.path.join(adir, n)))
                except Exception:
                    continue
                cn = d.get("_classname") or n[:-5]
                _ALPHA_CACHE[snake(cn)] = {
                    snake(f["_name"]) for f in d.get("_fields", []) if f.get("_name")}
    return _ALPHA_CACHE.get(snake(ndi_class), set())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ndi", default=os.environ.get("NDI_MATLAB_PATH", "/home/user/NDI-matlab"))
    ap.add_argument("--did", default=os.environ.get("DID_MATLAB_PATH", "/home/user/DID-matlab"))
    a = ap.parse_args()

    if not os.path.isdir(a.ndi):
        sys.exit("NDI-matlab not found at %s (pass --ndi)" % a.ndi)

    truth, ref = ndi_templates(a.ndi)
    if not truth:
        sys.exit("no NDI templates found under %s" % DDIR)

    div = v_alpha_divergence(truth)
    reads = migrator_reads(truth, a.did)
    wdeps, wscan = writer_dependencies(a.ndi, truth)
    prov = classify_divergence(a.ndi, ref, truth, {r["ndi_class"]: r for r in div})
    for r in div:
        r["provenance"] = prov.get(r["ndi_class"], {"verdict": "UNKNOWN"})

    doc = {
        "_comment": (
            "GROUND TRUTH for the did_v1 side of the V_eta migration: the NDI document "
            "templates, read from %s. THIS FILE IS AUTHORITATIVE -- schemas/V_alpha and the "
            "V_delta conversion markdown are history, not evidence. Where a template and its "
            "WRITER disagree, the writer wins (see writer_divergence): the data follows the "
            "writer. Regenerate with tools/ndi_ground_truth.py. See "
            "V_eta_ground_truth_plan.md." % ref),
        "ndi_ref": ref,
        "summary": {
            "ndi_classes": len(truth),
            "v_alpha_classes_compared": len(div) + sum(
                1 for c in truth if _alpha_names(c)) - len(div),
            "v_alpha_divergences": len(div),
            "migrator_suspects": len(reads),
            "migrator_suspects_confirmed_vocabulary": sum(
                1 for r in reads if r["confidence"] == "confirmed-vocabulary"),
            "writer_divergences": len(WRITER_DIVERGENCE),
            "writer_dependencies_no_template": len(wdeps),
            "writer_dependency_scan": wscan,
            "ndi_schema_document_scan": dict(SCHEMA_SCAN),
            "ndi_required_dependency_scan": dict(REQUIRED_SCAN),
            "provenance": {v: sum(1 for r in div if r["provenance"]["verdict"] == v)
                           for v in ("DID-INVENTED", "NDI-CHANGED", "UNKNOWN")},
        },
        "writer_divergence": WRITER_DIVERGENCE,
        "writer_dependencies": wdeps,
        "v_alpha_divergence": div,
        "migrator_reads": reads,
        "classes": truth,
    }
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=2, sort_keys=False)
        f.write("\n")

    print("ndi ref:                %s" % ref)
    print("NDI classes captured:   %d" % len(truth))
    print("V_alpha divergences:    %d" % len(div))
    print("migrator suspects:      %d" % len(reads))
    print("writer divergences:     %d (hand-recorded)" % len(WRITER_DIVERGENCE))
    pc = {v: sum(1 for r in div if r["provenance"]["verdict"] == v)
          for v in ("DID-INVENTED", "NDI-CHANGED", "UNKNOWN")}
    print("divergence provenance:  DID-INVENTED %d | NDI-CHANGED %d | UNKNOWN %d"
          % (pc["DID-INVENTED"], pc["NDI-CHANGED"], pc["UNKNOWN"]))
    # DENOMINATOR for the provenance walk (operating rule 5). The walk reads
    # ONLY `ref`, so this line says how many of the divergent classes it could
    # locate a first version for at all -- an UNKNOWN because the first template
    # predates the property-block format is a different fact from an UNKNOWN
    # because the walk never found the file, and the two used to print the same.
    nof = sum(1 for r in div
              if r["provenance"].get("why", "").startswith(("no add-commit",
                                                            "no ref to walk")))
    print("  DENOMINATOR: %d divergent class(es), walked on %s ONLY (no other "
          "ref is consulted)" % (len(div), ref))
    print("  first version located: %d   no add-commit found on %s: %d"
          % (len(div) - nof, ref, nof))
    # DENOMINATOR FIRST for the required-ness extract (operating rule 5). Every
    # line here exists so that a downstream zero is readable: "NDI requires no
    # edge V_eta relaxed" and "no class could be asked" print differently.
    rs = REQUIRED_SCAN
    print("")
    print("NDI DEPENDENCY REQUIRED-NESS (`mustbenotempty`), as NDI states it")
    print("  DENOMINATOR: %d NDI class(es) -- %d with a flat schema document, "
          "%d with a JSON Schema-form one, %d with none"
          % (rs["ndi_classes"], rs["classes_with_flat_schema_document"],
             rs["classes_with_json_schema_document"],
             rs["classes_with_no_schema_document"]))
    print("  DENOMINATOR: %d dependency name(s) -- %d carry an NDI required-ness "
          "statement, %d NDI states nothing about"
          % (rs["dependency_names_total"],
             rs["dependency_names_with_a_required_statement"],
             rs["dependency_names_ndi_states_nothing_about"]))
    print("  NDI REQUIRES: %d   NDI SAYS OPTIONAL: %d"
          % (rs["dependency_names_required"], rs["dependency_names_optional"]))
    print("  templates carrying `mustbenotempty`: %d  "
          "(the key lives in the SCHEMA documents, not the templates)"
          % rs["templates_carrying_mustbenotempty"])
    if rs["dependency_names_with_a_required_statement"] == 0:
        print("  *** NO CLASS STATED REQUIRED-NESS AT ALL. Every downstream")
        print("  *** count is then a property of this scan, not of NDI.")
    print("")
    print("wrote %s" % os.path.relpath(OUT, REPO))
    if reads:
        print("\nmigrators using vocabulary no NDI template has (confirm each individually):")
        for r in sorted(reads, key=lambda x: x["confidence"] != "confirmed-vocabulary"):
            mark = "!!" if r["confidence"] == "confirmed-vocabulary" else "? "
            names = r["reads_names_absent_from_template"] or r["mentions_names_absent_from_template"]
            print("  %s %-34s %s" % (mark, r["migrator"], names))
        print("\n  !! = read via an explicit idiom   ? = mentioned only (may be a comment)")


if __name__ == "__main__":
    main()
