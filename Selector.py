from rdflib import *
from rdflib import collection
from Namespaces import *
from Result import *
from LensMatch import *


# TODO: 
# Add support for fresnel:group
# Add support for fresnel:use
# Add support for fresnel:purpose
# Add support for multiple sublens
# Add support for alternate and merged properties

class Selector:
	""" This class will select only the properties need from the RDF resource by using the fresnel lens. """

	def __init__(self, fresnel, rdf_graph):
		self.fresnel = fresnel
		self.rdf_graph = rdf_graph
		self.lens_for_resource = {}

	def matchResource( self ):
		""" goes through all the lenses in fresnel data and matches lens with the appropriate resources from the RDF """
		for lens in self.fresnel.getLenses():
			lens_class, lens_instance = self.fresnel.getLensDomain( lens )
			for cl in lens_class:
				for resource in self.rdf_graph.subjects( predicate=rdf_ns['type'], object=cl ):
					if resource not in self.lens_for_resource:
						self.lens_for_resource[resource] = LensMatch(resource)
					
					self.lens_for_resource[resource].addClassLens( lens )
					if self.fresnel.isDefaultLens( lens ):
						self.lens_for_resource[resource].addDefaultLens( lens)
					if self.fresnel.isLabelLens( lens ):
						self.lens_for_resource[resource].addLabelLens( lens )

			all_subjects = self.rdf_graph.subjects()
			for resource in lens_instance:
				if resource in all_subjects:
					if resource not in self.lens_for_resource:
						self.lens_for_resource[resource] = LensMatch( resource )
					self.lens_for_resource[resource].addInstanceLens( lens )
					if self.fresnel.isDefaultLens( lens ):
						self.lens_for_resource[resource].addDefaultLens( lens )
					if self.fresnel.isLabelLens( lens ):
						self.lens_for_resource[resource].addLabelLens( lens )

	def resolveConflict( self, resource, lensMatch ):
		""" resolves conflicts when multiple lenses have been chosse for a resource """

		instance_lens = lensMatch.getInstanceLens()
		class_lens = lensMatch.getClassLens()
		default_lens = lensMatch.getDefaultLens()
		if len( instance_lens ) > 0:
			if len( instance_lens ) == 1:
				return instance_lens.pop()
			else:
				d = set.intersection( instance_lens, default_lens )
				if len(d) == 1:
					return d.pop()
				else:
					raise Exception("Unresolvable Lens conflict")
		elif len( class_lens ) > 0:
			if len( class_lens ) == 1:
				return class_lens.pop()
			else:
				#TODO: get the most specific class from all the classes
				d = set.intersection( class_lens, default_lens )
				if len(d) == 1:
					return d.pop()
				else:
					raise Exception("Unresolvable Lens conflict")
		raise Exception("Unresolvable Lens conflict...no lens found")
		return None


	def getProperties( self, lens, resource ):
		""" return a ordered list of all the properties to be displayed for the resource using the lens """
		
		properties = []
		
		super_lens = self.fresnel.getSuper( lens )

		for prop in self.fresnel.getShowProperties( lens ):
			if prop == fresnel_ns['allProperties']:
				for prop in self.rdf_graph.predicates( subject=resource ):
					properties.append( prop )
				break
			elif prop == fresnel_ns['super']:
				properties.extend( self.getProperties( super_lens, resource) )
			else:
				properties.append( prop )
	
		# hide property

		for prop in self.fresnel.getHideProperties( lens ):
			if prop in properties:
				properties.remove( prop )

		return properties
		

	def select( self ):
		self.matchResource()

		#Apply the lens to result
		self.result = [] #Will contain the properties that should be displayed for the resource according to the lens

		for resource in  self.lens_for_resource:
			lens = self.resolveConflict( resource, self.lens_for_resource[resource] )
			print "Lens:", lens
			new_resource = Resource( resource , lens)
			properties = self.getProperties( lens, resource )
			for property in properties:
				sublens = self.fresnel.getSublens( property )
				if sublens:
					new_sublens = Sublens( resource, lens, sublens, property )
					new_sublens.getPropertySet( self.fresnel, self.rdf_graph )
					new_resource.addProperty( new_sublens )
				else:
					if isinstance( property, BNode ):
						desc = property
						#TODO: clean up the code
						property = self.fresnel.fresnel_graph.value( subject=desc, predicate=fresnel_ns['property'] )
						if property:
							new_p = Property( subject = new_resource, property = property )
						else:
							alt_prop = self.fresnel.fresnel_graph.value( subject=desc, predicate=fresnel_ns['alternateProperties'] )
							if alt_prop:
								alt_prop = collection.Collection( self.fresnel.fresnel_graph, alt_prop )
								new_p = Property( subject = new_resource, alternate_property = alt_prop )
							else:
								merge_prop = self.fresnel.fresnel_graph.value( subject = desc, predicate=fresnel_ns['mergeProperties'] )
								if merge_prop:
									merge_prop = collection.Collection( self.fresnel.fresnel_graph , merge_prop )
									new_p = Property( subject = new_resource, merged_property = merge_prop )
								else:
									print "in lens ", lens
									raise Exception("No property mentioned in lens" )

						new_p.setPropertyDescription( desc )
					else:
						new_p = Property( subject = new_resource, property = property )
					new_resource.addProperty( new_p )
			self.result.append( new_resource )
