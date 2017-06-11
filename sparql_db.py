from SPARQLWrapper import SPARQLWrapper, JSON
import pycurl
import requests

ns = """
PREFIX rp: <http://www.semanticweb.org/abjb788/ontologies/2017/5/untitled-ontology-579#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dbc: <http://dbpedia.org/resource/Category:>
"""

clear_default_query = """CLEAR SILENT DEFAULT"""
clear_data_query = """CLEAR GRAPH <http://example/Artist>"""

queryString_1 = ns + """
SELECT ?Candidate ?CandidateSupport
WHERE
{?x rp:hasCandidateSupport ?CandidateSupport.
?x rdfs:label ?Candidate
}
        """

queryString_2 = ns + """
INSERT {?Argument1 rp:hasArgumentStatus rp:ArgumentPresent}
#SELECT DISTINCT ?name ?Artist2 ?Artist1
WHERE{
    ?Argument1 a rp:Musician.
    ?User rp:hasCD ?x.
    ?x rp:hasArtist ?Artist1.
        {GRAPH <http://example/Artist> {?Artist1 rdfs:label ?name}}

    SERVICE<http://dbpedia.org/sparql>
        {?Artist2 rdf:type dbo:MusicalArtist.
            ?Artist2 rdfs:label ?name
        }
}
"""

queryString_2a = ns + """
INSERT {?Argument1 rp:hasArgumentStatus rp:ArgumentPresent}
#SELECT DISTINCT ?name ?Artist2 ?Artist1
WHERE{
    ?Argument1 a rp:NonMusician.
    ?User rp:hasCD ?x.
    ?x rp:hasArtist ?Artist1.
        {GRAPH <http://example/Artist> {?Artist1 rdfs:label ?name}}

    SERVICE<http://dbpedia.org/sparql>
        {?Artist2 rdf:type dbo:Scientist.
            ?Artist2 rdfs:label ?name
        }
}
"""

queryString_3 = ns + """
INSERT {?Argument1 rp:hasArgumentStatus rp:ArgumentPresent}
#SELECT DISTINCT  ?Artist1 ?Artist2 ?name
WHERE{
    ?Argument1 a rp:ClassicalMusician.
    ?User rp:hasCD ?x.
    ?x rp:hasArtist ?Artist1.

  {GRAPH <http://example/Artist> {?Artist1 rdfs:label ?name}}

 SERVICE<http://dbpedia.org/sparql>
 {?Artist2 dct:subject dbc:18th-century_classical_composers.
  ?Artist2 rdfs:label ?name
  }
}
"""

queryString_4 = ns + """
INSERT {?Candidate rp:hasCandidateSupport ?CandidateSupport} 
WHERE
{ SELECT (SUM(?Weight) as ?CandidateSupport) ?Candidate
{
 		?Candidate ?property ?Argument.
        ?property rdfs:subPropertyOf rp:candidateArgumentProperties.
        ?Argument rp:hasWeight ?Weight.
        ?Argument rp:hasArgumentStatus rp:ArgumentPresent.
    }
    GROUP BY ?Candidate
}
"""

queryString_5 = ns + """
    select distinct ?Abstract ?Artist
    WHERE{
  	SERVICE <http://dbpedia.org/sparql/>
    {?A rdfs:label "%s"@en.
    ?A dbo:abstract ?Abstract.
    ?A foaf:isPrimaryTopicOf ?Artist.
    FILTER (lang(?Abstract)='en')
    }}
"""


class SPARQL_Query:
    sparql_q = SPARQLWrapper("http://localhost:3030/HierarchicalModel/query")
    sparql_u = SPARQLWrapper("http://localhost:3030/HierarchicalModel/update")
    model_upload = SPARQLWrapper("http://localhost:3030/HierarchicalModel/upload")

    def __init__(self):
        self.clear_graph(clear_default_query)
        self.clear_graph(clear_data_query)
        self.add_model()

    def decision_query(self):
        queryString = queryString_1
        SPARQL_Query.sparql_q.setQuery(queryString)

        SPARQL_Query.sparql_q.setReturnFormat(JSON)
        results = SPARQL_Query.sparql_q.query().convert()

        return results
        # for result in results["results"]["bindings"]:
        # print(result["Candidate"]["value"] + " ------ " + result["CandidateSupport"]["value"])

    def artist_abstract(self, artist_name):
        self.artist_name = artist_name
        queryString = queryString_5%artist_name
        SPARQL_Query.sparql_q.setQuery(queryString)

        SPARQL_Query.sparql_q.setReturnFormat(JSON)
        abstract = SPARQL_Query.sparql_q.query().convert()

        return abstract

    def clear_graph(self, queryString):
        self.queryString = queryString
        SPARQL_Query.sparql_u.setQuery(self.queryString)
        SPARQL_Query.sparql_u.method = 'POST'
        SPARQL_Query.sparql_u.query()

    def add_model(self):
        model = open("Musician.ttl", "rb")
        headers = {'Content-type': 'text/turtle'}
        url = 'http://localhost:3030/HierarchicalModel/data'
        r = requests.post(url, data=model, headers=headers)
        # print(r.text)

    def add_graph(self, artist_name):
        self.artist_name = artist_name
        queryString = ns + """INSERT {GRAPH <http://example/Artist> {?Artist1 rdfs:label "%s"@en}} WHERE{?Artist1 rdf:type rp:Artist}""" % artist_name
        SPARQL_Query.sparql_u.setQuery(queryString)
        SPARQL_Query.sparql_u.method = 'POST'
        SPARQL_Query.sparql_u.query()

    def insert_model_queries(self, queryString):
        self.queryString = queryString
        SPARQL_Query.sparql_u.setQuery(self.queryString)
        SPARQL_Query.sparql_u.method = 'POST'
        SPARQL_Query.sparql_u.query()

    def do_all_inserts(self):
        self.insert_model_queries(queryString_2)
        self.insert_model_queries(queryString_2a)
        self.insert_model_queries(queryString_3)
        self.insert_model_queries(queryString_4)



        # q = SPARQL_Query()
        # #
        # q.add_graph('Wolfgang Amadeus Mozart')
        # q.do_all_inserts()
        # results = q.decision_query()
        #
        # for result in results["results"]["bindings"]:
        #             print(result["Candidate"]["value"] + " ------ " + result["CandidateSupport"]["value"])

# q = SPARQL_Query()
# results = q.artist_abstract('George Harrison')
# for result in results["results"]["bindings"]:
#     print(result["Abstract"]["value"] + " ------ " + result["Artist"]["value"])