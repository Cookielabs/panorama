from Namespaces import *
from rdflib import *

class Resource:

	def __init__( self, uri, lens ):
		self.uri = uri
		self.lens = lens
		self.property_set = []
	
	def setLens( self, lens ):
		self.lens = lens

	def setFormat( self, format ):
		self.format = format
	
	def addProperty( self, property ):
		self.property_set.append( property )
	
	def render( self ):
		string ="<div id='Resource'>\n"
		for property in self.property_set:
			string +=  property.render( self.uri )
		string +="</div>\n"
		return string

class Property:

	def __init__( self,  property, subject ):
		self.property = property
		self.for_subject = subject
		self.values = []
		self.desc = None

	def setFormat( self, format ):
		self.format = format
	
	def setLabel( self, label ):
		self.label = label
	
	def addValue( self, value ):
		self.values.append( value )
	
	def setPropertyDescription( self, desc ):
		self.desc = desc

	def render( self , resource_uri):
		if len( self.values ) > 0 :
			string = "<div id='property'>"
			if self.label:
				string += "<div id='label'>" + str(self.label).title() + "</div>"
			for value in self.values:
				string += "<div id='value'>" + value + "</div>"
			string += "</div>\n"
		else:
			string = "Property discarded " + self.property + "\n"
		return string

class Sublens:

	def __init__( self, uri, superlens, sublens, lens_uri):
		self.uri = uri
		self.superlens = superlens
		self.sublens = sublens
		self.lens_uri = lens_uri # A BNode which has type propertyDescription

	def setSuperLens( self, lens ):
		self.superlens = lens

	def setLabel( self, label ):
		self.label = label

 	def getProperties( self, lens, resource , fresnel, rdf_graph):
                """ return a ordered list of all the properties to be displayed for the resource using the lens """

                properties = []

                super_lens = fresnel.getSuper( lens )
                if super_lens:
                        properties.extend( self.getProperties( super_lens, resource, fresnel, rdf_graph ) )

                for prop in fresnel.getShowProperties( lens ):
                        if prop == fresnel_ns['allProperties']:
                                for prop in rdf_graph.predicates( subject=resource ):
                                        properties.append( prop )
                                break
			elif prop == fresnel_ns['super']:
                                properties.extend( self.getProperties( super_lens, resource) )
                        else:
                                properties.append( prop )

                # hide property

                for prop in fresnel.getHideProperties( lens ):
                        if prop in properties:
                                properties.remove( prop )

                return properties
	
	def getPropertySet( self, fresnel, rdf_graph):
		self.property_set = []

		self.property = fresnel.fresnel_graph.value( subject=self.lens_uri, predicate = fresnel_ns['property'] )

		for resource in rdf_graph.objects( subject= self.uri, predicate = self.property ):
			new_resource = Resource( resource, self.sublens )
			properties = self.getProperties( self.sublens, resource , fresnel, rdf_graph)
			print "SSS", resource, properties
			for property in properties:
				sublens = fresnel.getSublens( property )
				if sublens:
					new_sublens = Sublens( resource, self.lens, sublens, property )
					new_sublens.getPropertySet( fresnel, rdf_graph )
					new_resource.addProperty( new_sublens )
				else:
					if isinstance( property, BNode ):
                                                desc = property
                                                property = self.fresnel.fresnel_graph.value( subject=desc, predicate=fresnel_ns['property'] )
						new_p = Property( property, new_resource )
                                                new_p.setPropertyDescription( desc )
                                        else:   
                                                new_p = Property( property , new_resource )
					new_resource.addProperty( new_p )
			self.property_set.append( new_resource )

	def render( self, resource_uri ):
		string = "<div id='sublens'>\n"
		if self.label:
			string += "<div label>" + self.label + "</div>\n"
		for resource in self.property_set:
			string += resource.render( )
		string += "</div>\n"
		return string
