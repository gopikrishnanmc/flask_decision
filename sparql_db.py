from SPARQLWrapper import SPARQLWrapper, JSON
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
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX snomed-term: <http://purl.bioontology.org/ontology/SNOMEDCT/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX fhir: <http://hl7.org/fhir/>
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

queryString_6 = ns + """
INSERT {?s rdf:type snomed-term:247472004}
WHERE{
?s fhir:Coding.code ?code.
  ?s fhir:Coding.system ?system.
  ?s rdf:type ?type.
}

"""

queryString_7 = ns + """
SELECT ?div
WHERE{

?s fhir:Narrative.div ?div
}

"""

queryString_8 = ns + """
SELECT DISTINCT ?y ?label1
WHERE{
?s rdf:type ?type.
SERVICE <http://sparql.bioontology.org/sparql?apikey=179ba070-35eb-4bbd-a33a-e8d4f5686cf9>{
    ?type rdfs:subClassOf ?y.
    ?y skos:prefLabel  ?label1.
  }}
"""

queryString_9 = ns + """
SELECT DISTINCT ?x ?label2 
WHERE{
?s rdf:type ?type.
SERVICE <http://sparql.bioontology.org/sparql?apikey=179ba070-35eb-4bbd-a33a-e8d4f5686cf9>{
    ?x rdfs:subClassOf ?type.
    ?x skos:prefLabel  ?label2.}
}
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

class FHIR_query():
    sparql_q = SPARQLWrapper("http://localhost:3030/FHIR/query")
    sparql_u = SPARQLWrapper("http://localhost:3030/FHIR/update")

    def __init__(self):
        self.clear_graph(clear_default_query)
        self.add_patient_data()
        self.insert_queries(queryString_6)

    def clear_graph(self, queryString):
        self.queryString = queryString
        FHIR_query.sparql_u.setQuery(self.queryString)
        FHIR_query.sparql_u.method = 'POST'
        FHIR_query.sparql_u.query()

    def add_patient_data(self):
        model = open("allergyintolerance-medication.ttl", "rb")
        headers = {'Content-type': 'text/turtle'}
        url = 'http://localhost:3030/FHIR/data'
        r = requests.post(url, data=model, headers=headers)

    def insert_queries(self, queryString):
        self.queryString = queryString
        FHIR_query.sparql_u.setQuery(self.queryString)
        FHIR_query.sparql_u.method = 'POST'
        FHIR_query.sparql_u.query()

    def patient_data_query(self):
        queryString = queryString_7
        FHIR_query.sparql_q.setQuery(queryString)
        FHIR_query.sparql_q.setReturnFormat(JSON)
        results = FHIR_query.sparql_q.query().convert()
        return results

    def patient_data_query_2(self):
        queryString = queryString_8
        FHIR_query.sparql_q.setQuery(queryString)
        FHIR_query.sparql_q.setReturnFormat(JSON)
        results = FHIR_query.sparql_q.query().convert()
        return results

    def patient_data_query_3(self):
        queryString = queryString_9
        FHIR_query.sparql_q.setQuery(queryString)
        FHIR_query.sparql_q.setReturnFormat(JSON)
        results = FHIR_query.sparql_q.query().convert()
        return results

# q = FHIR_query()
# results = q.patient_data_query()
# results_2 = q.patient_data_query_2()
# results_3 = q.patient_data_query_3()
# for result in results["results"]["bindings"]:
#     print(result["div"]["value"])
#
# for result in results_2["results"]["bindings"]:
#     print(result["label1"]["value"])
#
# for result in results_3["results"]["bindings"]:
#     print(result["label2"]["value"])