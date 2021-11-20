import requests
import json
import datetime

sparql_url = 'http://localhost:8890/sparql?graph-uri=https://synbiohub.org/public'
blazegraph_url = "http://localhost:8889/bigdata/sparql"
jena_url = "http://localhost:3030/igem/sparql?graph=https://synbiohub.org/public"

f = open('dominant-twins.json',)
dominant_twins = json.load(f).get('results').get('bindings')
dominant_twin_list = [] # list of all dominant twins
dominant_twin_roles = {} # roles of above twins in K/V format, K = URI, V = identifiers.org role
dominant_twin_role_name = {} #K = URI, v = "RBS"

for p in dominant_twins:
	dominant_twin_list.append(p.get('s').get('value'))

for p in dominant_twin_list:
	params = dict(
		query = """
PREFIX sbol: <http://sbols.org/v2#>

select ?role where {
  <"""+ p + """> sbol:role ?role
          }""",
          format = 'json'
		)
	response = requests.get(url = sparql_url, params = params).json()
	dominant_twin_roles[p] = (response.get('results').get('bindings')[0].get('role').get('value')) #http://identifiers.org/so/SO:0000139
	urisplit = response.get('results').get('bindings')[1].get('role').get('value').split("/")
	dominant_twin_role_name[p] = urisplit[len(urisplit) - 1]

virtuoso_query_time = datetime.timedelta(0, 0)
virtuoso_role_counter = 0


# Search virtuoso using roles
for p in dominant_twin_roles:
	params = dict(
		query = """
PREFIX sbol: <http://sbols.org/v2#>

select ?s where {
  ?s a sbol:ComponentDefinition .
  ?s sbol:role <"""+ dominant_twin_roles[p] + """>
          }""",
          format = 'json'
		)
	response = requests.get(url = sparql_url, params = params)
	virtuoso_query_time += response.elapsed
	for r in response.json().get('results').get('bindings'):
		virtuoso_role_counter += 1
		if r.get('s').get('value') == p:
			break

print("Virtuoso query time total: " + str(virtuoso_query_time))
sparql_role_average = float(virtuoso_role_counter) / len(dominant_twin_roles)
print("Sparql role average: " + str(sparql_role_average))

