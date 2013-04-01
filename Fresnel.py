from rdflib import *
from Namespaces import *
from rdflib import collection

class Fresnel:
	""" This class object will contain the fresnel data. """

	def __init__( self, fresnel_data ):
		""" fresnel_data var will contain the data in n3 format """
		self.fresnel_graph = Graph()
		self.fresnel_graph.parse( data = fresnel_data,  format="n3" )
		
		self.lenses = []
		self.formats = []
		self.label_lens = []

		for lens in self.fresnel_graph.subjects( predicate=rdf_ns['type'] , object= fresnel_ns['Lens']):
			self.lenses.append( lens )

		for format in self.fresnel_graph.subjects( predicate=rdf_ns['type'], object=fresnel_ns['Format']):
			self.formats.append( format )

		for lens in self.lenses:
			purposes = set( self.fresnel_graph.objects( subject=lens, predicate=fresnel_ns['purpose'] ) )
			if fresnel_ns['labelLens'] in purposes:
				self.label_lens.append( lens )
		#DEBUG
		for term in self.fresnel_graph:
			print term
	
	def getLensDomain( self, lens ):

		# Add support for SPARQL and FSL
		class_domain = []
		for type in self.fresnel_graph.objects( subject=lens, predicate=fresnel_ns['classLensDomain']):
			class_domain.append(type)

		instance_domain = []
		for type in self.fresnel_graph.objects( subject=lens, predicate=fresnel_ns['instanceLensDomain']):
			instance_domain.append(type)

		return class_domain, instance_domain

	def getShowProperties( self, lens ):
		
		for prop in self.fresnel_graph.objects( subject= lens, predicate=fresnel_ns['showProperties']):
				p = collection.Collection( self.fresnel_graph, prop )
				return list(p) 
		return []
	
	def getHideProperties( self, lens ):
		for prop in self.fresnel_graph.objects( subject = lens, predicate=fresnel_ns['hideProperties']):
			p = collection.Collection( self.fresnel_graph, prop )
			return list(p)

		return []

	def getGraph( self ):
		return self.fresnel_graph

	def getLenses( self ):
		return self.lenses

	def getFormats( self ):
		return self.formats

	def getSuper( self, lens ):
		return self.fresnel_graph.value( subject=lens, predicate=fresnel_ns['extends'] )


	def getSublens( self, resource ): #return None if the resource does not contain sublens
		return self.fresnel_graph.value( subject = resource, predicate=fresnel_ns['sublens'] )

	
	def getPropertyFormat( self, property ):
		return set( self.fresnel_graph.subjects( predicate=fresnel_ns['propertyFormatDomain'], object= property ) )
	
	def getLabelLens( self ):
		return self.label_lens
	
	
	def getLabelStyle( self, format ):
		# style can be both class as well as instructions
		styles = self.fresnel_graph.objects( subject=format, predicate=fresnel_ns['labelStyle'] )
		return list( styles )
	
	def getPropertyStyle( self, format ):
		
		styles = self.fresnel_graph.objects( subject=format, predicate=fresnel_ns['propertyStyle'] )
		return list( styles )

	def getValueStyle( self, format ):
		styles = self.fresnel_graph.objects( subject=format, predicate=fresnel_ns['valueStyle'] )
		return list( styles )

	def isDefaultLens( self, lens ):
		s = self.fresnel_graph.value( subject = lens, predicate=fresnel_ns['purpose'] )
		if s == fresnel_ns['defaultLens']:
			return True
		else:
			return False
	
	def isLabelLens( self, lens ):
		if lens in self.label_lens:
			return True
		else:
			return False

