import requests
import json
import datetime

#sparql_url = 'http://localhost:8890/sparql?graph-uri=https://synbiohub.org/public'
blazegraph_url = "http://localhost:8889/bigdata/sparql"
#jena_url = "http://localhost:3030/igem/sparql?graph=https://synbiohub.org/public"

f = open('dominant-twins.json',)
dominant_twins = json.load(f).get('results').get('bindings')
dominant_twin_list = [] # list of all dominant twins
dominant_twin_sequences = {} # sequences of above twins in K/V format, K = URI, V = Sequence

for p in dominant_twins:
	dominant_twin_list.append(p.get('s').get('value'))

seq_time = datetime.timedelta(0, 0)
# Get sequences for all dominant twins
for p in dominant_twin_list:
	params = dict(
		query = """PREFIX sbol: <http://sbols.org/v2#>
		select ?seq where {
  <""" + p + """> sbol:sequence ?seqUri .
  ?seqUri sbol:elements ?seq }""",
  		format = 'json'
		)
	response = requests.get(url = blazegraph_url, params = params)
	dominant_twin_sequences[p] = (response.json().get('results').get('bindings')[0].get('seq').get('value'))
	seq_time += response.elapsed

print("Sequence total query time: " + str(seq_time))

valid_twins = {} # Twins that hada sequence that virtuoso could handle
query_time = datetime.timedelta(0, 0) # Time our queries
sparql_exact_counter = 0 # Position in list of response from virtuoso
size_dict = {}
len_dict = {}
for p in dominant_twin_sequences:
	params = dict(
		query = """PREFIX sbol: <http://sbols.org/v2#>
		select ?s where {
		?s sbol:sequence ?seqUri .
		?seqUri sbol:elements \"\"\"""" + dominant_twin_sequences[p] + "\"\"\"}",
  		format = 'json'
		)
	response = requests.post(url = blazegraph_url, params = params)
	if 'application/sparql-results+json' in response.headers.get('content-type'):
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
