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
		self.property_label = {} # for caching data

	def resolveFormat( self, property ):
		
		#check if property has format associated with it using fresnel lens
		if isinstance(property, Property) and property.desc:
			uses = self.fresnel.fresnel_graph.objects( subject = property.desc, predicate = fresnel_ns['use'] ) # fresnel:use can link to group
			for use in uses:
				use_types = list( self.fresnel.fresnel_graph.objects( subject = use, predicate = rdf_ns['type'] ) )
				if fresnel_ns['format'] in use_types:
					format = use
					return format

		if isinstance(property, Resource ):
			resource = property.uri
			instance_formats = self.fresnel.fresnel_graph.subjects( predicate = fresnel_ns['instanceFormatDomain'], object = resource )
			matches = []
			for format in instance_formats:
				matches.append( format )

			if len( matches ) > 0: # TODO:resolve conflict
				return matches[0]
			#TODO: What if resource not in rdf_graph
			types = list( self.rdf_graph.objects( subject=resource, predicate=rdf_ns['type'] ) )
			
			#TODO: Can make it more efficient
			for type in types:
				formats = list( self.fresnel.fresnel_graph.subjects( predicate = fresnel_ns['classFormatDomain'], object = type ) )
				for format in formats:
					matches.append( format )
			if len( matches ) > 0: #TODO: resolve confict
				return matches[0]	
			return None

		#otherwise
		if isinstance( property, URIRef ):
			p = property
		else:
			if property.property:
				p = property.property
			elif property.alternate_property:
				p = property.alternate_property[0]
			elif property.merged_property:
				p = property.merged_property[0]
			else:
				raise("This shouldnt happen")
	
		formats = self.fresnel.getPropertyFormat( p )
                if len( formats ) > 1:
                        raise Exception("AAHHHHH!! More than one format for a property")
                if len( formats ) > 0:
                        format = formats.pop()
               	else:
                        format = None
		return format


	def matchFormat( self , resource):

		format_resource = self.resolveFormat( resource )
		self.applyResourceFormat( resource , format_resource)
		for property in resource.property_set:
			if isinstance( property, Sublens ):
				format = self.resolveFormat( property )
				self.applySublensFormat( property, format )
				for sub_resource in property.property_set:
					self.matchFormat( sub_resource )
			elif isinstance( property, Property ):
				format = self.resolveFormat( property )
				print "format", property.property, format
				self.applyPropertyFormat( property, format )
			else:
				raise Exception("THIS SHOULDNT HAPPEN")
	
	def applyResourceStyles( self, resource, format ):

		if format is None:
			return
		
		resource_styles = list(self.fresnel.fresnel_graph.objects( subject=format, predicate=fresnel_ns['resourceStyle'] ) )

		resource.setResourceStyle( resource_styles )

	
	def applyResourceFormat( self, resource, format ):

		if format is None:
			return

		#TODO

	def applyPropertyStyles( self, property, format ):
		if format is None:
			return
		#TODO: check foaf:group for styles
		property.label_style = self.fresnel.getLabelStyle( format )
		property.value_style = self.fresnel.getValueStyle( format )
		property.property_style = self.fresnel.getPropertyStyle( format )


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
		self.applyPropertyStyles( sublens, format )

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
			if property.property:
				print "for property ", property.property
				label = self.resolvePropertyLabel( property.property )
			else:
				#TODO: What if the first property does not have label
				if property.alternate_property:
					p = property.alternate_property[0]
				elif property.merged_property:
					p = property.merged_property[0]
				else:
					raise Exception("Oops! Now What?")
				label = self.resolvePropertyLabel( p )
		property.setLabel(label)

		self.getValues( property, format )
		self.applyPropertyStyles( property, format )

		value_formats = self.fresnel.fresnel_graph.objects( subject=format, predicate=fresnel_ns['valueFormat'] )

		for f in value_formats:
			for p, o in self.fresnel.fresnel_graph.predicate_objects( subject=f ):
				property.value_format[ p ] = o

		property_formats = self.fresnel.fresnel_graph.objects( subject=format, predicate=fresnel_ns['propertyFormat'] )

		for f in property_formats:
			for p, o in self.fresnel.fresnel_graph.predicate_objects( subject=f ):
				property.property_format[ p ] = o
	 
	
	def getValues( self, property, format ):
		if property.property:
			self.getPropertyValues( property.property, format, property )
		elif property.alternate_property:
			self.alternateProperties( property, format )
		elif property.merged_property:
			self.mergeProperties( property, format )
		else:
			raise Exception("Property not found..")

	def getPropertyValues( self, property, format, property_class ):	
		print "Getting values for ", property, "..."
		value_type = self.fresnel.fresnel_graph.value( subject=format, predicate=fresnel_ns['value'] )
		values = self.rdf_graph.objects( subject=property_class.for_subject.uri, predicate=property )
		flag = False
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
				flag = True
				property_class.addValue( string )
		return flag

	def alternateProperties( self, property, format ):
		if property.alternate_property is None:
			return
		flag = False
		for p in property.alternate_property:
			flag = self.getPropertyValues( p , format , property)
			if flag:
				break
			else:
				print "Trying next alternate..."
	
	def mergeProperties( self, property, format ):
		if property.merged_property is None:
			return
		for p in property.merged_property:
			self.getPropertyValues( p, format, property )
	
		
			
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
			print "downloading...", resource
			new_graph = Graph()
			new_graph.load(resource)
			print "done"
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

