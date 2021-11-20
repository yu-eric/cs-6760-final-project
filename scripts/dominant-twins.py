import requests

virtuoso_url = "http://localhost:8890/sparql"
#blazegraph_url = "http://localhost:8889/bigdata/sparql"
#jena_url = "http://localhost:3030/igem/sparql"
params = dict(
		query = """select ?s from <https://synbiohub.org/public> where {
  ?s <http://wiki.synbiohub.org/wiki/Terms/igem#dominant> "true"}""",
  		format = 'json'
		)
        # Change this url based on triplestore being hit
response = requests.post(url = virtuoso_url, params = params)
print(str(response.elapsed))