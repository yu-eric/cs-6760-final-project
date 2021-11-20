import requests
import json
import datetime

sparql_url = 'http://localhost:8890/sparql'

f = open('dominant-twins.json',)
dominant_twins = json.load(f).get('results').get('bindings')
dominant_twin_list = [] # list of all dominant twins
dominant_twin_sequences = {} # sequences of above twins in K/V format, K = URI, V = Sequence

for p in dominant_twins:
	dominant_twin_list.append(p.get('s').get('value'))

# Get sequences for all dominant twins
for p in dominant_twin_list:
	params = dict(
		query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX sbol: <http://sbols.org/v2#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX purl: <http://purl.obolibrary.org/obo/>select ?seq where {
  <""" + p + """> sbol:sequence ?seqUri .
  ?seqUri sbol:elements ?seq }""",
  		format = 'json'
		)
	response = requests.get(url = sparql_url, params = params).json()
	dominant_twin_sequences[p] = (response.get('results').get('bindings')[0].get('seq').get('value'))

valid_twins = {} # Twins that hada sequence that virtuoso could handle
query_time = datetime.timedelta(0, 0) # Time our queries
sparql_exact_counter = 0 # Position in list of response from virtuoso
size_dict = {}
len_dict = {}
for p in dominant_twin_sequences:
	params = dict(
		query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX sbol: <http://sbols.org/v2#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX purl: <http://purl.obolibrary.org/obo/>select ?s where {
  ?s sbol:sequence ?seqUri .
  ?seqUri sbol:elements \"\"\"""" + dominant_twin_sequences[p] + "\"\"\"}",
  		format = 'json'
		)
	response = requests.post(url = sparql_url, params = params)
	if response.headers.get('content-type') == 'application/sparql-results+json':
		valid_twins[p] = dominant_twin_sequences[p]
		jsresp = response.json().get('results').get('bindings')
		len_dict[len(jsresp)] = len_dict.get(len(jsresp), 0) + 1
		query_time += response.elapsed
		for r in jsresp:
			size_dict[len(jsresp)] = size_dict.get(len(jsresp), 0) + 1
			if r.get('s').get('value') == p:
				break

print("Normal list size: " + str(len(dominant_twin_sequences)) + "    Filtered list length: " + str(len(valid_twins)))
print("Total query time: " + str(query_time))
#sparql_exact_average = float(sparql_exact_counter) / len(valid_twins)
#print("Sparql exact average: " + str(sparql_exact_average))
for key in size_dict:
  print(str(key) + ', ' + str(size_dict[key] / float(len_dict[key])))

# _____________ SEQUENCE SEARCH _______________
seq_search_time = datetime.timedelta(0, 0)
seq_search_exact_counter = 0
size_dict = {}
len_dict = {}

seq_search_url = 'http://localhost:13162'
for p in valid_twins:
	params = {
		'query': """PREFIX sbol2: <http://sbols.org/v2#>
	}
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>

SELECT DISTINCT
    ?subject
    ?displayId
    ?version
    ?name
    ?description
    ?type

WHERE {
    ?subject sbol2:sequence ?seq .
    ?seq sbol2:elements \"""" + valid_twins[p] + """\".
 # flag_search_exact: True

    ?subject a ?type .
    ?subject sbh:topLevel ?subject
    OPTIONAL { ?subject sbol2:displayId ?displayId . }
    OPTIONAL { ?subject sbol2:version ?version . }
    OPTIONAL { ?subject dcterms:title ?name . }
    OPTIONAL { ?subject dcterms:description ?description . }
} """,
  		'default-graph-uri': 'https://synbiohub.org/public'
		}
	response = requests.get(url = seq_search_url, params = params)
	if response.headers.get('content-type') == 'application/json':
		jsresp = response.json().get('results').get('bindings')
		seq_search_time += response.elapsed
		len_dict[len(jsresp)] = len_dict.get(len(jsresp), 0) + 1
		for r in jsresp:
			size_dict[len(jsresp)] = size_dict.get(len(jsresp), 0) + 1
			seq_search_exact_counter += 1
			if r.get('subject').get('value') == p:
				break
	
print("Total query time: " + str(seq_search_time))
#seq_average = float(seq_search_exact_counter) / len(valid_twins)
#print("Sequence search average: " + str(seq_average))	
for key in size_dict:
  print(str(key) + ', ' + str(size_dict[key] / float(len_dict[key])))


