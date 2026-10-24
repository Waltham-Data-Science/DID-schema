"""A CURIE's prefix is written the way its issuer cites it.

Signed 2026-10-19, V_eta_prefix_spelling_plan.md, TEAM-SIGN-OFF [prefix spelling]:
"a CURIE's prefix is written as its issuer cites it (the registry entry's spelling:
ORCID:, ROR:, PMID:, PMCID:, RRID:, doi:, WormBase:, EDAM:format_), for identifiers
and term nodes alike; readers match a prefix by key, spelling or synonym, ignoring
case; registry keys stay the lowercase Bioregistry prefixes."

Built by tools/build_v_eta.py section 6b. These tests read the BUILT schema.
"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
VETA = os.path.join(HERE, "..", "schemas", "V_eta")
META_FILES = {"did_schema_meta.json", "CURIE_lookups_meta.json", "ndi_reserved_keys.json",
              "binding_registry_meta.json", "term_registry_meta.json", "class_disposition_meta.json"}


def _load(p):
    with open(p) as fh:
        return json.load(fh)


def _registry():
    return _load(os.path.join(VETA, "stable", "CURIE_lookups_meta.json"))


def _prefixes():
    return _registry()["prefixes"]


def test_every_entry_has_a_spelling_a_source_and_synonyms():
    px = _prefixes()
    assert len(px) >= 41, f"only {len(px)} registry entries read"
    for key, e in px.items():
        assert isinstance(e.get("spelling"), str) and e["spelling"], key
        assert isinstance(e.get("spelling_source"), str) and e["spelling_source"], key
        assert isinstance(e.get("synonyms"), list), key
        assert all(isinstance(s, str) and s for s in e["synonyms"]), key


def test_keys_stay_the_lowercase_bioregistry_prefixes():
    for key in _prefixes():
        assert key == key.lower(), key


def test_a_spelling_is_its_key_a_synonym_or_the_entry_it_is_written_as():
    """The spelling is the same word as the key in another case (`NCBITaxon`),
    a name Bioregistry lists for the entry (`PMID` for `pubmed`), or, for an
    entry cited through another one, that entry's spelling (`RRID`)."""
    px = _prefixes()
    for key, e in px.items():
        sp = e["spelling"]
        if "written_as" in e:
            target = e["written_as"]["prefix"]
            assert target in px, (key, target)
            assert sp == px[target]["spelling"], (key, sp)
            assert e["written_as"]["id_prefix"], key
            continue
        names = {key.lower()} | {s.lower() for s in e["synonyms"]}
        assert sp.lower() in names, (key, sp)


def test_obo_spellings_are_the_id_space_in_uri_base():
    """Plan sec. 3: "OBO PURL" spellings are the capitalisation of the ID space
    in the entry's own `uri_base`, so they are checked mechanically."""
    n = 0
    for key, e in _prefixes().items():
        m = re.fullmatch(r"https?://purl\.obolibrary\.org/obo/([A-Za-z]+)_",
                         e.get("uri_base") or "")
        if m is None:
            continue
        n += 1
        assert e["spelling"] == m.group(1), (key, e["spelling"], m.group(1))
    assert n >= 15, f"only {n} OBO PURL entries read -- the check inspected too little"


def test_no_two_entries_share_a_name():
    """Plan P2: no two entries may share a key, spelling or synonym, ignoring case.
    A `written_as` entry's spelling belongs to the entry it is written as."""
    seen = {}
    for key, e in _prefixes().items():
        names = [key] + e["synonyms"]
        if "written_as" not in e:
            names.append(e["spelling"])
        if "legacy_rewrite" in e:
            names.append(e["legacy_rewrite"]["legacy_prefix"])
        for n in names:
            other = seen.setdefault(n.lower(), key)
            assert other == key, f"{n!r} names both {other!r} and {key!r}"


def test_the_signed_spellings():
    px = _prefixes()
    signed = {"orcid": "ORCID", "ror": "ROR", "pubmed": "PMID", "pmc": "PMCID",
              "rrid": "RRID", "doi": "doi", "wormbase": "WormBase", "edam": "EDAM",
              "ncbitaxon": "NCBITaxon", "om": "om"}
    assert len(signed) == 10
    for key, sp in signed.items():
        assert px[key]["spelling"] == sp, (key, px[key]["spelling"])
    assert px["cellosaurus"]["written_as"] == {"prefix": "rrid", "id_prefix": "CVCL_"}
    assert px["addgene"]["written_as"] == {"prefix": "rrid", "id_prefix": "Addgene_"}
    assert px["wormbase"]["legacy_rewrite"] == {"legacy_prefix": "WBStrain",
                                                "id_prefix": "WBStrain"}
    assert px["edam"]["legacy_rewrite"] == {"legacy_prefix": "format",
                                            "id_prefix": "format_"}
    assert "NCBIT" in px["ncbitaxon"]["synonyms"]
    assert {"pmid", "PMID"} <= set(px["pubmed"]["synonyms"])
    assert "PMCID" in px["pmc"]["synonyms"]


def test_the_new_entries_of_section_3a():
    px = _prefixes()
    for key in ("om", "edam", "efo", "pubchem.compound", "snomedct", "ncim", "ndic",
                "fbdv"):
        assert key in px, key
    assert px["pubchem.compound"]["spelling"] == "PubChem"
    assert px["ncim"]["spelling"] == "NCIm"
    assert px["ndic"]["spelling"] == "NDIC"
    assert px["fbdv"]["spelling"] == "FBdv"


def test_the_registry_says_how_prefixes_are_written():
    d = _registry()["description"]
    assert ("Prefixes are matched case-insensitively and written as each entry's "
            "`spelling`, the form the identifier's issuer cites.") in d
    assert "written in lowercase" not in d


def _spelling_index():
    return {e["spelling"] for e in _prefixes().values() if "written_as" not in e}


def _nodes(blob, out):
    if isinstance(blob, dict):
        for k, v in blob.items():
            if k in ("node", "root_node") and isinstance(v, str):
                out.append(v)
            else:
                _nodes(v, out)
    elif isinstance(blob, list):
        for v in blob:
            _nodes(v, out)


def test_every_node_in_the_built_schema_uses_its_spelling():
    """Plan P3: term nodes follow the rule too. Every CURIE `node` / `root_node` in
    the class files and the binding registry starts with an entry's spelling,
    exactly (not a key in another case, not a synonym)."""
    spellings = _spelling_index()
    files = [p for p in glob.glob(os.path.join(VETA, "*", "*.json"))
             if os.path.basename(p) not in META_FILES - {"binding_registry_meta.json"}]
    nodes = []
    for p in files:
        _nodes(_load(p), nodes)
    curies = [n for n in nodes if re.match(r"^[A-Za-z][A-Za-z0-9_.]*:", n)
              and not n.startswith(("http:", "https:"))]
    assert len(files) > 100 and len(curies) > 50, (len(files), len(curies))
    bad = sorted({n for n in curies if n.split(":", 1)[0] not in spellings})
    assert not bad, bad


def test_global_identifier_examples_use_the_spelling():
    ent = _load(os.path.join(VETA, "stable", "entity.json"))
    doc = next(f for f in ent["fields"] if f["name"] == "global_identifier")
    text = json.dumps(doc)
    assert "'ORCID:0000-0002-1825-0097'" in text
    assert "'WormBase:WBStrain00000001'" in text
    assert "'orcid:" not in text and "'wormbase:" not in text
