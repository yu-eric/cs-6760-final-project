import requests

# virtuoso_url = "http://localhost:8890/sparql"
blazegraph_url = "http://localhost:8889/bigdata/sparql"
#jena_url = "http://localhost:3030/igem/sparql"
params = dict(
		query = "SELECT (COUNT(?s) AS ?triples) from <https://synbiohub.org/public> WHERE { ?s ?p ?o }",
  		format = 'json'
		)
        # Change this url based on triplestore being hit
response = requests.post(url = blazegraph_url, params = params)
print(str(response.elapsed))