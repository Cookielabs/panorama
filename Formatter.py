from Result import *
from rdflib import *

#TODO:
#Add support for styling

class Formatter:


	def __init__( self, selector ):
		self.selector = selector
		self.fresnel = selector.fresnel
		self.rdf_graph = selector.rdf_graph
		self.result = selector.result
		self.property_label = {}

	def resolveFormat( self, property ):
		
		#check if property has format associated with it using fresnel lens
		if isinstance(property, Property) and property.desc:
			uses = self.fresnel.fresnel_graph.objects( subject = property.desc, predicate = fresnel_ns['use'] ) # fresnel:use can link to group
			for use in uses:
				use_types = list( self.fresnel.fresnel_graph.objects( subject = use, predicate = rdf_ns['type'] ) )
				if fresnel_ns['format'] in use_types:
					format = use
					return format

		#otherwise
		formats = self.fresnel.getPropertyFormat( property.property )
                if len( formats ) > 1:
                        raise Exception("AAHHHHH!! More than one format for a property")
                if len( formats ) > 0:
                        format = formats.pop()
               	else:
                        format = None
		return format

	def matchFormat( self , resource):

		for property in resource.property_set:
			if isinstance( property, Sublens ):
				format = self.resolveFormat( property )
				self.applySublensFormat( property, format )
				for sub_resource in property.property_set:
					self.matchFormat( sub_resource )
			elif isinstance( property, Property ):
				format = self.resolveFormat( property)
				self.applyPropertyFormat( property, format )
				print "format", property.property, format
			else:
				raise Exception("THIS SHOULDNT HAPPEN")
	
	def applySublensFormat( self, sublens , format):

		#set only the label.

		label = self.fresnel.fresnel_graph.value(subject=format, predicate=fresnel_ns['label'] )

		if label is not None:
			if isinstance( label,  Literal ):
				sublens.setLabel( label.title() )
			if label == fresnel_ns['none']:
				sublens.setLabel(None)
		else:
			label = self.resolvePropertyLabel( sublens.property )
			sublens.setLabel(label)
		print "s l", sublens.label
		
	def applyPropertyFormat( self, property, format ):
		property.setFormat( format )
		
		#get label - if fresnel:label is not specified then Resolve Label using the rdf_graph
		label = self.fresnel.fresnel_graph.value(subject=format, predicate=fresnel_ns['label'] )

		if label is not None:
			if isinstance( label,  Literal ):
				 label = label.title() 
			if label == fresnel_ns['none']:
				 label = None
		else:
			label = self.resolvePropertyLabel( property.property )
		property.setLabel(label)

		value_type = self.fresnel.fresnel_graph.value( subject=format, predicate=fresnel_ns['value'] )
		values = self.rdf_graph.objects( subject=property.for_subject.uri, predicate=property.property )

		print "Getting values..", property.property
		for value in values:
			string = ""
			if value_type is not None:
				if value_type == fresnel_ns['image']:
					#TODO:check value is image src or uri to src like foaf:image
					string = "<img src=\"" + value + "\" alt=\"" + value + "\" />"
				if value_type == fresnel_ns['externalLink']:
					string = "<a href=\"" + value + "\">" + value + "</a>"
				if value_type == fresnel_ns['uri']:
					string = value 
			else:
				if isinstance( value, Literal ):
					#check if 'en' otherwise skip
					if value.language:
						if value.language != "en":
							continue
					string = value
				else:
					string = self.resolveValueLabel( value )
			print string
			if string:
				property.addValue( string )
	
	def resolvePropertyLabel( self, property ):
		print "Resolving label for property ", property
		if property in self.property_label:
			return self.property_label[property]
		new_graph = Graph()
		new_graph.load( property )
		labels = new_graph.objects( subject=property, predicate=rdfs_ns['label'] )
		for label in labels:
			if label.language:
				if label.language != "en":
					continue
			new_graph.close()
			self.property_label[property] = label
			return label
		return None

	def resolveValueLabel( self, resource ):
		#TODO: support for labelLens in fresnel
		if resource in self.selector.lens_for_resource:
			label_lens = self.selector.lens_for_resource[resource].getLabelLens()
			#TODO: resolve conflict for multiple label lens
			label_len = label_lens.pop()
			property = self.fresnel.fresnel_graph.value( subject=label_len, predicate=fresnel_ns['showProperties'] )
			if property is None:
				raise Exception("No property specified for label lens")
			value = self.rdf_graph.value( subject=resource, predicate=property )
			if value:
				return value

		#check if rdf label exists inside the current graph
		labels = self.rdf_graph.objects( subject=resource, predicate=rdfs_ns['label'] )
		for label in labels:
			if label.language:
				if label.language != "en":
					continue
			return label
		#if is not BNode then try getting from outside source
		if isinstance( resource, URIRef ):
			new_graph = Graph()
			new_graph.load(resource)
			#check if any labelLens match the resource
			labelLens = self.fresnel.getLabelLens()
			types = list( new_graph.objects( subject=resource, predicate=rdf_ns['type'] ) )
			property = None
			#TODO: resolve conflict for multiple label lens
			for lens in labelLens:
				class_domain, instance_domain = self.fresnel.getLensDomain( lens )
				for instance in instance_domain:
					if instance == resource:
						property = self.fresnel.fresnel_graph.value( subject=lens, predicate=fresnel_ns['showProperties'] )
						if property is None:
							raise Exception("No property specified for label lens")
						break
				if property is not None:
					break
				for cl in class_domain:
					if cl in types:
						property = self.fresnel.fresnel_graph.value( subject=lens, predicate=fresnel_ns['showProperties'] )
						break
				if property is not None:
					break
			if property is not None:
				value = new_graph.value(subject=resource, predicate=property )
				if value:
					return value

			#check for default label ie rdfs:label
			labels = new_graph.objects( subject=resource, predicate=rdfs_ns['label'] )
		        for label in labels:
                       		if label.language:
                                	if label.language != "en":
						continue
				new_graph.close()
                        	return label

	def format( self ):

		for resource in self.result:
			self.matchFormat( resource )

