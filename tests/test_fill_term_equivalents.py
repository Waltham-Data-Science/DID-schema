"""tools/fill_term_equivalents.py: only EXACT equivalents are written.

The rule ([equivalents filled in did-schema], building on [term equivalents
recorded]): an equivalent means the same thing as the term. From OLS4 that is
skos:exactMatch, owl:equivalentClass to a named IRI, or an xref whose axiom
says it is exact; an unqualified oboInOwl:hasDbXref is NOT (NCBITaxon:562 xrefs
a PubMed id), nor is any close/broad/narrow/related match. These tests build
the entities by hand, so they do not share the premise of OLS's own output.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import fill_term_equivalents as fte

CURIES = fte.Curies({"prefixes": {
    "ncbitaxon": {"spelling": "NCBITaxon", "uri_style": "obo_underscore",
                  "uri_base": "http://purl.obolibrary.org/obo/NCBITaxon_", "synonyms": ["taxon"]},
    "ncit": {"spelling": "NCIT", "uri_style": "obo_underscore",
             "uri_base": "http://purl.obolibrary.org/obo/NCIT_", "synonyms": ["NCIt"]},
    "pubmed": {"spelling": "PMID", "uri_style": "direct",
               "uri_base": "https://www.ncbi.nlm.nih.gov/pubmed/", "synonyms": ["pubmed"]},
    "wikidata": {"spelling": "wikidata", "uri_style": "direct",
                 "uri_base": "http://www.wikidata.org/entity/", "synonyms": []},
    "openminds": {"spelling": "openminds", "uri_style": "direct",
                  "uri_base": "https://openminds.om-i.org/instances/", "synonyms": []},
    "allen_ccf_v3": {"spelling": "allen_ccf_v3", "uri_style": "local", "uri_base": ""},
}})


def row(name, node, eq=()):
    return {"name": name, "node": node, "equivalent": list(eq)}


def test_exact_kinds_are_counted():
    e = {
        fte.SKOS_EXACT: ["http://www.wikidata.org/entity/Q25419"],
        fte.OWL_EQUIVALENT: "http://purl.obolibrary.org/obo/NCIT_C14206",
        fte.HAS_DBXREF: [{"value": "NCIt:C1", "axioms": [{fte.XREF_SOURCE: "MONDO:equivalentTo"}]}],
    }
    exact, left = fte.exact_from_entity(e)
    assert exact == ["http://www.wikidata.org/entity/Q25419",
                     "http://purl.obolibrary.org/obo/NCIT_C14206", "NCIt:C1"]
    assert sum(left.values()) == 0


def test_loose_matches_are_left_out():
    e = {
        fte.HAS_DBXREF: ["PMID:10319482", "GC_ID:11",
                         {"value": "NCIT:C2", "axioms": [{fte.XREF_SOURCE: "BIRNLEX:1748"}]}],
        "http://www.w3.org/2004/02/skos/core#closeMatch": ["http://www.wikidata.org/entity/Q1"],
        "http://www.w3.org/2004/02/skos/core#broadMatch": "http://www.wikidata.org/entity/Q2",
        "http://www.w3.org/2004/02/skos/core#relatedMatch": ["http://www.wikidata.org/entity/Q3"],
        fte.OWL_EQUIVALENT: {"type": ["class expression"]},
    }
    exact, left = fte.exact_from_entity(e)
    assert exact == []
    assert left["oboInOwl:hasDbXref without an exact qualifier"] == 3
    assert left["skos:closeMatch"] == 1 and left["skos:broadMatch"] == 1
    assert left["skos:relatedMatch"] == 1
    assert left["owl:equivalentClass to a class expression"] == 1


def test_written_in_registry_spelling_and_round_trips():
    assert CURIES.from_value("NCIt:C14206") == "NCIT:C14206"
    assert CURIES.from_value("http://purl.obolibrary.org/obo/NCIT_C14206") == "NCIT:C14206"
    assert CURIES.from_value("MESH:D004926") is None          # prefix not registered
    assert CURIES.from_value("http://unece.org/vocab#TradeProduct") is None
    assert CURIES.iri("allen_ccf_v3:385") is None              # local prefix: no IRI
    assert CURIES.iri("") is None


def test_r13_refuses_own_node_other_rows_node_and_shared_claims():
    rows = [row("E. coli", "NCBITaxon:562"), row("Escherichia coli (NCIT)", "NCIT:C14206"),
            row("a", "NCIT:C1"), row("b", "NCIT:C2"), row("c", "NCIT:C3", ["wikidata:Q9"])]
    proposals = {
        0: ["NCBITaxon:562", "NCIT:C14206", "wikidata:Q25419"],   # own node; another row's node; ok
        2: ["wikidata:Q7"], 3: ["wikidata:Q7"],                    # one id, two rows
        4: ["wikidata:Q9"],                                        # already held
    }
    adds, refused = fte.apply_r13(rows, proposals, CURIES)
    assert dict(adds) == {0: ["wikidata:Q25419"]}
    assert len(refused) == 3
    assert any('registered as "Escherichia coli (NCIT)"' in r for r in refused)
    assert sum("also claimed by" in r for r in refused) == 2


def test_openminds_preferred_identifier_both_directions(tmp_path):
    sp = tmp_path / "species"
    sp.mkdir()
    (sp / "musMusculus.jsonld").write_text(json.dumps({
        "@id": "https://openminds.om-i.org/instances/species/musMusculus",
        "preferredOntologyIdentifier": "http://purl.obolibrary.org/obo/NCBITaxon_10090",
        "otherOntologyIdentifier": ["http://purl.obolibrary.org/obo/NCIT_C45247"]}))
    (sp / "rattus.jsonld").write_text(json.dumps({
        "@id": "https://openminds.om-i.org/instances/species/rattusNorvegicus",
        "preferredOntologyIdentifier": "http://purl.obolibrary.org/obo/NCBITaxon_10116"}))
    rows = [row("Mus musculus", "NCBITaxon:10090"), row("mouse (NCIT)", "NCIT:C45247"),
            row("rat", "openminds:species/rattusNorvegicus")]
    out, stats = fte.openminds_candidates(rows, CURIES, str(tmp_path), ["species"])
    assert dict(out) == {0: ["openminds:species/musMusculus"], 2: ["NCBITaxon:10116"]}
    # otherOntologyIdentifier is counted, never written
    assert stats["otherOntologyIdentifier matches (not read: left for the team)"] == 1


def test_dry_run_writes_nothing_and_prints_denominator_first(tmp_path, capsys):
    reg = tmp_path / "reg.json"
    reg.write_text(json.dumps({"terms": [row("x", "NCIT:C1")]}, indent=2) + "\n")
    cur = tmp_path / "cur.json"
    cur.write_text(json.dumps({"prefixes": CURIES.prefixes}))
    before = reg.read_text()
    fte.main(["--registry", str(reg), "--curies", str(cur)])
    out = capsys.readouterr().out
    assert out.startswith("DENOMINATOR\n  rows read")
    assert "OLS4: NOT MEASURED" in out and "openMINDS: NOT MEASURED" in out
    assert reg.read_text() == before
