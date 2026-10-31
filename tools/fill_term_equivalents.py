#!/usr/bin/env python3
"""Fill the term registry's `equivalent` column from openMINDS and OLS4.

Decision: Jess Haley, 2026-10-30, V_eta_go_forward_class_audit.md
[equivalents filled in did-schema] ("B"): the `equivalent` column of
schemas/registry/did_v2_term_registry.json ([term equivalents recorded]) is filled by a
one-time did-schema data change, made by a did-schema script and reviewed in
its PR. "The first fill is the species rows from openMINDS's species
instances." This is that script.

An equivalent is an id in another vocabulary that means the SAME thing as the
term ([term equivalents recorded]). Nothing broader, narrower or merely
related is written. The rule, per source:

  openMINDS (--openminds DIR, the decided first fill)
      An openMINDS terminology instance is an equivalent of the registry row
      whose node is the instance's `preferredOntologyIdentifier`: openMINDS
      declares that ontology term to be the instance's own identifier. Read
      the other way, a registry row whose node IS an openMINDS instance takes
      that instance's preferredOntologyIdentifier. The instance is written `openminds:<terminology>/<instance>` (the form
      NCBITaxon:6239's row already carries, [species text is the openMINDS
      equivalent]). `otherOntologyIdentifier` is NOT read: it is counted and
      left for the team. --openminds-terminologies picks the terminology
      folders; the default is `species`, the decided first fill.

  ols (--ols)
      From the term's DEFINING ontology in OLS4 only (an importing ontology's
      copy is not read), looked up by the term's IRI (CURIE_lookups_meta.json):
        * skos:exactMatch                                       -> counted
        * owl:equivalentClass to a named IRI (not an expression) -> counted
        * oboInOwl:hasDbXref ONLY when the xref's axiom annotation
          qualifies it as exact (EXACT_XREF_QUALIFIERS, e.g. Mondo's
          `MONDO:equivalentTo`)                                 -> counted
      NOT counted: an unqualified hasDbXref (OBO uses it for citations,
      genetic codes and loose matches: NCBITaxon:562 xrefs PMID:10319482 and
      GC_ID:11; UBERON:0002436 xrefs two FMA ids), skos:closeMatch,
      broadMatch, narrowMatch, relatedMatch, synonyms, and alternative ids.

Every source, then (check_term_registry.py rule R13): the id must be in a
prefix the CURIE registry knows, written in its spelling, and must round-trip
(the CURIE expands back to the IRI it came from); it is never the row's own
node, never another row's node (that would be two rows for one meaning, R1;
reported, not written), and never claimed by two rows (an id two terms both
claim is exact for at most one of them; reported, not written).

Denominator first, always: rows read, rows looked up, rows with no IRI,
lookups failed. A row whose lookup failed, or that the source does not define,
is NOT MEASURED; it is never reported as "no equivalents".

Default is a dry run that writes nothing. --write adds the ids to the
registry (existing ids are kept; nothing is removed). OLS responses are cached
in --cache-dir (keyed by IRI) so a re-run reads the same answers.

Usage:
  python3 tools/fill_term_equivalents.py --openminds <openMINDS_instances>/instances/latest/terminologies \\
      --ols --cache-dir <scratch>/ols-cache [--write]
"""
import argparse
import glob
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "schemas", "registry", "did_v2_term_registry.json")
CURIES = os.path.join(ROOT, "schemas", "registry", "CURIE_lookups_meta.json")
OLS_API = "https://www.ebi.ac.uk/ols4/api/v2/entities"

SKOS_EXACT = "http://www.w3.org/2004/02/skos/core#exactMatch"
OWL_EQUIVALENT = "http://www.w3.org/2002/07/owl#equivalentClass"
HAS_DBXREF = "http://www.geneontology.org/formats/oboInOwl#hasDbXref"
XREF_SOURCE = "http://www.geneontology.org/formats/oboInOwl#source"
# An xref is exact only when its axiom annotation says so.
EXACT_XREF_QUALIFIERS = {"MONDO:equivalentTo", "skos:exactMatch", SKOS_EXACT}
# Read so they can be counted as left out; never written.
NOT_EXACT = {
    "http://www.w3.org/2004/02/skos/core#closeMatch": "skos:closeMatch",
    "http://www.w3.org/2004/02/skos/core#broadMatch": "skos:broadMatch",
    "http://www.w3.org/2004/02/skos/core#narrowMatch": "skos:narrowMatch",
    "http://www.w3.org/2004/02/skos/core#relatedMatch": "skos:relatedMatch",
}
EXPANDING_STYLES = ("obo_underscore", "direct", "fragment")


# --------------------------------------------------------------- CURIEs / IRIs

class Curies:
    """CURIE <-> IRI through CURIE_lookups_meta.json, in the registry's spelling."""

    def __init__(self, meta):
        self.prefixes = meta.get("prefixes", {})
        self.names = {}
        for key, e in self.prefixes.items():
            for n in [key, e.get("spelling") or ""] + list(e.get("synonyms") or []):
                if n:
                    self.names.setdefault(n.lower(), key)

    def _entry(self, prefix):
        key = self.names.get(prefix.lower())
        return key, (self.prefixes.get(key) if key else None)

    def iri(self, curie):
        """The IRI a CURIE expands to, or None (empty node, local/approximate prefix)."""
        pre, sep, local = (curie or "").strip().partition(":")
        if not sep or not local:
            return None
        _, e = self._entry(pre)
        if not e or e.get("approximate") or e.get("uri_style") not in EXPANDING_STYLES:
            return None
        return (e.get("uri_base") or "") + local if e.get("uri_base") else None

    def norm(self, curie):
        """`curie` written in the registry's spelling, or None for an unknown prefix."""
        pre, sep, local = (curie or "").strip().partition(":")
        if not sep or not local:
            return None
        key, e = self._entry(pre)
        if not e:
            return None
        return f"{e.get('spelling') or key}:{local}"

    def key(self, curie):
        """The comparison key check_term_registry uses: registry key + local id."""
        pre, _, local = (curie or "").strip().partition(":")
        key, _ = self._entry(pre)
        return f"{key}:{local}" if key and local else None

    def from_value(self, value):
        """An IRI or CURIE from OLS, as a registry CURIE that round-trips, or None."""
        value = (value or "").strip()
        if value.startswith(("http://", "https://")):
            best = None
            for key, e in self.prefixes.items():
                base = e.get("uri_base") or ""
                if (base and value.startswith(base) and len(value) > len(base)
                        and e.get("uri_style") in EXPANDING_STYLES and not e.get("approximate")
                        and (best is None or len(base) > len(best[1]))):
                    best = (key, base)
            if not best:
                return None
            cur = f"{self.prefixes[best[0]].get('spelling') or best[0]}:{value[len(best[1]):]}"
            return cur if self.iri(cur) == value else None
        cur = self.norm(value)
        return cur if cur and self.iri(cur) else None


# ------------------------------------------------------------------ openMINDS

def openminds_candidates(rows, curies, base, terminologies):
    """{row index: [openminds CURIE]} from preferredOntologyIdentifier, plus counts."""
    by_iri = {}
    for i, t in enumerate(rows):
        iri = curies.iri(t.get("node"))
        if iri:
            by_iri.setdefault(iri, i)
    out, stats = defaultdict(list), Counter()
    folders = sorted(os.listdir(base)) if terminologies == ["all"] else terminologies
    for term in folders:
        files = sorted(glob.glob(os.path.join(base, term, "*.jsonld")))
        stats["terminology folders read"] += 1
        stats["instances read"] += len(files)
        for f in files:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            iid = d.get("@id") or ""
            if "/instances/" not in iid:
                continue
            cur = "openminds:" + iid.split("/instances/", 1)[1]
            pref = d.get("preferredOntologyIdentifier")
            if pref and pref in by_iri:
                if cur not in out[by_iri[pref]]:
                    out[by_iri[pref]].append(cur)
                stats["instances whose preferredOntologyIdentifier is a registry node"] += 1
            # The same statement read the other way: a row whose node IS the
            # instance takes the instance's preferredOntologyIdentifier.
            if iid in by_iri and pref:
                pc = curies.from_value(pref)
                if pc:
                    if pc not in out[by_iri[iid]]:
                        out[by_iri[iid]].append(pc)
                    stats["registry openMINDS rows whose instance names a preferredOntologyIdentifier"] += 1
                else:
                    stats["preferredOntologyIdentifier in a prefix the CURIE registry cannot write"] += 1
            for other in d.get("otherOntologyIdentifier") or []:
                if other in by_iri:
                    stats["otherOntologyIdentifier matches (not read: left for the team)"] += 1
    return out, stats


# ------------------------------------------------------------------------ OLS

def ols_fetch(iri, cache_dir, retries=3):
    """OLS4 v2 entities for `iri` (cached), or raise."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, urllib.parse.quote(iri, safe="") + ".json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    url = OLS_API + "?" + urllib.parse.urlencode({"iri": iri, "size": 100})
    err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.load(r)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
            return data
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
            err = e
            time.sleep(1 + 2 * attempt)
    raise RuntimeError(f"{type(err).__name__}: {err}")


def _values(v):
    return v if isinstance(v, list) else ([] if v is None else [v])


def exact_from_entity(entity):
    """(exact values, {left-out kind: n}) from one OLS4 v2 entity, by the rule above."""
    exact, left = [], Counter()
    for v in _values(entity.get(SKOS_EXACT)):
        val = v.get("value") if isinstance(v, dict) else v
        if isinstance(val, str):
            exact.append(val)
    for v in _values(entity.get(OWL_EQUIVALENT)):
        val = v.get("value") if isinstance(v, dict) else v
        if isinstance(val, str):
            exact.append(val)
        else:
            left["owl:equivalentClass to a class expression"] += 1
    for v in _values(entity.get(HAS_DBXREF)):
        if isinstance(v, dict) and isinstance(v.get("value"), str):
            quals = set()
            for ax in _values(v.get("axioms")):
                if isinstance(ax, dict):
                    for q in _values(ax.get(XREF_SOURCE)):
                        if isinstance(q, str):
                            quals.add(q)
            if quals & EXACT_XREF_QUALIFIERS:
                exact.append(v["value"])
                continue
        left["oboInOwl:hasDbXref without an exact qualifier"] += 1
    for prop, name in NOT_EXACT.items():
        left[name] += len(_values(entity.get(prop)))
    return exact, left


def ols_candidates(rows, curies, cache_dir, workers=4):
    """{row index: [CURIE]}, per-row status, and left-out counts."""
    from concurrent.futures import ThreadPoolExecutor

    status, out, left, unmapped = {}, defaultdict(list), Counter(), Counter()
    todo = []
    for i, t in enumerate(rows):
        iri = curies.iri(t.get("node"))
        if iri:
            todo.append((i, iri))
        else:
            status[i] = "no IRI"

    def one(item):
        i, iri = item
        try:
            return i, iri, ols_fetch(iri, cache_dir), None
        except RuntimeError as e:
            return i, iri, None, str(e)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, iri, data, err in ex.map(one, todo):
            if err:
                status[i] = f"lookup failed ({err})"
                continue
            defining = [e for e in data.get("elements", [])
                        if e.get("isDefiningOntology") and e.get("iri") == iri]
            if not defining:
                status[i] = "not defined in OLS4"
                continue
            status[i] = "measured"
            for e in defining:
                vals, lo = exact_from_entity(e)
                left.update(lo)
                for val in vals:
                    cur = curies.from_value(val)
                    if not cur:
                        unmapped[val.split(":")[0] if not val.startswith("http") else val] += 1
                    elif cur not in out[i]:
                        out[i].append(cur)
    return out, status, left, unmapped


# ---------------------------------------------------------------- the filter

def apply_r13(rows, proposals, curies):
    """Keep the proposed ids R13 allows; return (adds, refused lines)."""
    node_of = {}
    for i, t in enumerate(rows):
        k = curies.key(t.get("node"))
        if k:
            node_of[k] = i
    held = {}
    for i, t in enumerate(rows):
        for e in t.get("equivalent") or []:
            held[curies.key(e)] = i
    claims = defaultdict(set)
    for i, ids in proposals.items():
        for cur in ids:
            claims[curies.key(cur)].add(i)
    adds, refused = defaultdict(list), []
    for i in sorted(proposals):
        t = rows[i]
        own = curies.key(t.get("node"))
        for cur in proposals[i]:
            k = curies.key(cur)
            name = t.get("name")
            if k == own:
                continue
            if k in node_of:
                refused.append(f'{t.get("node")} "{name}": {cur} is registered as '
                               f'"{rows[node_of[k]].get("name")}" (two rows for one meaning?)')
            elif k in held and held[k] != i:
                refused.append(f'{t.get("node")} "{name}": {cur} is already an equivalent of '
                               f'"{rows[held[k]].get("name")}"')
            elif len(claims[k]) > 1:
                others = sorted(rows[j].get("name") for j in claims[k] if j != i)
                refused.append(f'{t.get("node")} "{name}": {cur} is also claimed by {others}')
            elif k in held:
                continue
            elif cur not in adds[i]:
                adds[i].append(cur)
    return adds, refused


# ----------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--openminds", metavar="DIR",
                    help="openMINDS_instances instances/latest/terminologies folder")
    ap.add_argument("--openminds-terminologies", default="species",
                    help="comma-separated terminology folders, or 'all' (default: species)")
    ap.add_argument("--ols", action="store_true", help="read exact equivalents from OLS4")
    ap.add_argument("--cache-dir", default=os.path.join(
        os.environ.get("TMPDIR", "/tmp"), "did-schema-ols-cache"))
    ap.add_argument("--registry", default=REGISTRY)
    ap.add_argument("--curies", default=CURIES)
    ap.add_argument("--write", action="store_true", help="update the registry (default: dry run)")
    a = ap.parse_args(argv)

    with open(a.registry, encoding="utf-8") as fh:
        reg = json.load(fh)
    with open(a.curies, encoding="utf-8") as fh:
        curies = Curies(json.load(fh))
    rows = reg.get("terms", [])
    with_iri = sum(1 for t in rows if curies.iri(t.get("node")))

    proposals, sources = defaultdict(list), defaultdict(dict)
    print("DENOMINATOR")
    print(f"  rows read                         {len(rows)}")
    print(f"  rows with an IRI                  {with_iri}")
    print(f"  rows with no IRI (staged or local) {len(rows) - with_iri}")
    print(f"  rows already carrying an equivalent {sum(1 for t in rows if t.get('equivalent'))}")

    if a.openminds:
        terms = [s.strip() for s in a.openminds_terminologies.split(",") if s.strip()]
        om, st = openminds_candidates(rows, curies, a.openminds, terms)
        print(f"  openMINDS: terminologies {','.join(terms)}; " +
              "; ".join(f"{k} {v}" for k, v in st.items()))
        for i, ids in om.items():
            for c in ids:
                proposals[i].append(c)
                sources[i][c] = "openMINDS"
    else:
        print("  openMINDS: NOT MEASURED (no --openminds folder)")

    if a.ols:
        ol, status, left, unmapped = ols_candidates(rows, curies, a.cache_dir)
        sc = Counter(s if not s.startswith("lookup failed") else "lookup failed" for s in status.values())
        print(f"  OLS4: rows looked up {with_iri}; measured {sc['measured']}; "
              f"not defined in OLS4 {sc['not defined in OLS4']} (NOT MEASURED); "
              f"lookups failed {sc['lookup failed']} (NOT MEASURED); no IRI {sc['no IRI']}")
        nm = Counter(rows[i]["node"].split(":")[0] for i, s in status.items() if s != "measured" and s != "no IRI")
        print("    not measured, by prefix: " + ", ".join(f"{k} {v}" for k, v in nm.most_common()))
        print("    left out as not exact: " + (", ".join(f"{k} {v}" for k, v in left.most_common()) or "none"))
        print("    exact ids in a prefix the CURIE registry cannot write: " +
              (", ".join(f"{k} {v}" for k, v in unmapped.most_common()) or "none"))
        for i, s in sorted(status.items()):
            if s.startswith("lookup failed"):
                print(f"    FAILED {rows[i]['node']}: {s}")
        for i, ids in ol.items():
            for c in ids:
                if c not in proposals[i]:
                    proposals[i].append(c)
                    sources[i][c] = "OLS4"
    else:
        print("  OLS4: NOT MEASURED (no --ols)")

    adds, refused = apply_r13(rows, proposals, curies)
    by_prefix = Counter(c.split(":")[0] + " via " + sources[i][c] for i, ids in adds.items() for c in ids)
    print("RESULT")
    print(f"  rows gaining an equivalent        {len(adds)}")
    print(f"  ids added                         {sum(len(v) for v in adds.values())}")
    for k, v in by_prefix.most_common():
        print(f"    {k:40s} {v}")
    print(f"  ids refused by R13                {len(refused)}")
    for r in refused:
        print(f"    REFUSED {r}")
    for i in sorted(adds):
        print(f'  ADD {rows[i]["node"]} "{rows[i]["name"]}": {adds[i]}')

    if a.write and adds:
        for i, ids in adds.items():
            rows[i]["equivalent"] = list(rows[i].get("equivalent") or []) + ids
        with open(a.registry, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(reg, indent=2, ensure_ascii=False) + "\n")
        print(f"WROTE {a.registry}")
    elif a.write:
        print("nothing to write")
    else:
        print("dry run: nothing written (--write to apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
