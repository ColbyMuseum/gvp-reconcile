"""
gvpquery: class for SPARQL queries against the GVP endpoint, base class for AATQuery and ULANQuery.
"""
import requests, abc

#TODO 0: Wire in as a SparqlWrapper subclass or with a SPARQLQuery property 
class GVPQuery:
	
	def __init__(self, candidate_term):
		self.url_base = 'http://vocab.getty.edu/sparql.json'
		self.seed_term = candidate_term
		self.prefLabel = ""
		self.URL = ""
		self.conceptID = ""
		self.query_results = dict()
	
	@abc.abstractmethod
	def reconcile(self):
		# Stub for subclass
		print "Unimplemented!"

class AATQuery(GVPQuery):

	def reconcile(self):
		# TODO 2: Refactor the SPARQL query to optimize--need more info for recon?
		# AAT sparql query: search by lucene index (a somewhat fuzzy search), 
		# minus the activities facet, and then filtered for entries that are either 
		# objects or materials, then finds exact matches in gvp:term.

		sparql_query = 'select ?entry ?label { ?entry luc:term ?seed_term ; gvp:prefLabelGVP/xl:literalForm ?label . filter exists { ?entry (xl:prefLabel|xl:altLabel)/gvp:term ?term. filter (lcase(str(?term)) = ?seed_term)}}'.replace("?seed_term",self.seed_string.lower())

		# Send the HTTP request, parse from JSON.
		# TODO 1: should raise HTTP errs

		query_response = requests.get(self.url_base, params={'query': sparql_query})
		response_json = query_response.json()
		results = response_json['results']['bindings'] # strip header from response

		if not results:
			print "No matches found. Bummer!"
		else:	
			#TODO 0: Now that this is "automated", how will we choose a match? Who is supervising recon?
			#TODO 0: Should the extant recons be used as training? As a lookup table?
			self.query_results = results
			self.URL = results[0]['entry']['value']
			self.conceptID = self.URL.split('/')[-1]
			self.prefLabel = results[0]['label']['value']

class ULANQuery(GVPQuery):

	def reconcile(self):
		sparql_query = "select ?entry ?name {?entry (skos:prefLabel|skos:altLabel) '%s'. ?entry skos:prefLabel ?name}".replace( "?seed_term", self.seed_string.lower()) 

		query_response = requests.get(self.url_base, params={'query': sparql_query})
		response_json = query_response.json()
		results = response_json['results']['bindings']
		if not results:
			print "Searched for '%s'. No matches found." % self.seed_string
		else:
			self.query_results = results
			self.URL = results[0]['entry']['value']
			self.conceptID = self.URL.split('/')[-1]
			self.prefLabel = results[0]['name']['value']
			print "Entry URI: %s | concept ID: %s | prefLabel: %s " % (self.URL, self.conceptID, self.prefLabel) 

