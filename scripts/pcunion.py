import requests

#virtuoso_url = "http://localhost:8890/sparql"
blazegraph_url = "http://localhost:8889/bigdata/sparql"
#jena_url = "http://localhost:3030/igem/sparql"
params = dict(
		query = """PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>
		SELECT DISTINCT ?parent ?child
		WHERE
		{
			?parent sbh:topLevel ?parent .
			?child sbh:topLevel ?child .
			{ ?parent ?oneLink ?child } UNION { ?parent ?twoLinkOne ?tmp . ?tmp ?twoLinkTwo ?child }
		}""",
  		format = 'json'
		)
        # Change this url based on triplestore being hit
response = requests.post(url = blazegraph_url, params = params)
print(str(response.elapsed))