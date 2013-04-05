from Namespaces import *
from rdflib import *



def renderStyle( styles ):
	if styles is None:
		return " "
	class_styles = []
	instruction_styles = []
	for style in styles:
		if style.datatype == fresnel_ns['styleClass']:
			class_styles.append( style )
		if style.datatype == fresnel_ns['stylingInstructions']:
			instruction_styles.append( style )
	string = ""
	if len(class_styles) > 0:
		if len( class_styles ) == 1:
			class_style = class_styles[0]
			string +="class='"+class_style+"' "
		else:
			#TODO: resolve issue or get first style option?
			class_style  = class_styles[0]
			string +="class='"+class_style+"' "  
		
	if len( instruction_styles ) > 0:
		string +="style='"
		for style in instruction_styles:
			string += style
		string +="' "
	return string

class Resource:

	def __init__( self, uri, lens ):
		self.uri = uri
		self.lens = lens
		self.property_set = []
		self.resource_styles = None

		self.property_format = None

	def setLens( self, lens ):
		self.lens = lens

	def setFormat( self, format ):
		self.format = format
	
	def setResourceStyle( self, styles ):
		self.resource_styles = styles 

	def addProperty( self, property ):
		self.property_set.append( property )
	
	def render( self ):
		string ="<div id='resource' " + renderStyle( self.resource_styles ) +">\n"
		for property in self.property_set:

			if self.property_set.index( property ) == 0:
				string += property.render( first=True, last=False )
			elif self.property_set[-1] == property:
				string +=  property.render( first=False, last=True )
			else:
				string += property.render( first=False, last=False )
	
		string +="</div>\n"
		return string

	def renderTable( self ):
		string = "<table id='resource'>\n"
		for property in self.property_set:
			string += property.renderTable()
		string +="</table>\n"
		return string

class Property:

	def __init__( self,  property, subject ):
		self.property = property
		self.for_subject = subject
		self.values = []
		self.desc = None
		
		self.label_style = None
		self.property_style = None
		self.value_style = None

		self.value_format = {}
		self.property_format = {}

	def setFormat( self, format ):
		self.format = format
	
	def setLabel( self, label ):
		self.label = label
	
	def addValue( self, value ):
		self.values.append( value )
	
	def setPropertyDescription( self, desc ):
		self.desc = desc
	
	def setLabelStyle( self, style ):
		self.label_style = style
	
	def setPropertyStyle( self, style ):
		self.property_style = style

	def setValueStyle( self, style ):
		self.value_style = style

	def render( self , first, last):
		string = ""
		pf_content = self.property_format[ fresnel_ns['contentBefore'] ] if fresnel_ns['contentBefore'] in self.property_format else ""
		if first:
			if fresnel_ns['contentFirst'] in self.property_format:
				pf_ciontent = self.property_format[ fresnel_ns['contentFirst'] ]
		string += pf_content
		
		string += "<div id='property' " + renderStyle( self.property_style ) + ">\n"
	
		if len( self.values ) > 0 :
			if self.label:
				string += "<label "+ renderStyle( self.label_style ) + ">" + str(self.label).title() + "</label>\n"
			string +="<div id='value' " + renderStyle( self.value_style ) + ">"
			for value in self.values:
				f_content = self.value_format[ fresnel_ns['contentBefore'] ] if fresnel_ns['contentBefore'] in self.value_format else ""
				if self.values.index( value ) == 0:
					if fresnel_ns['contentFirst'] in self.value_format:
						f_content = self.value_format[ fresnel_ns['contentFirst'] ]
				string += f_content
				string += value
				l_content = self.value_format[ fresnel_ns['contentAfter'] ] if fresnel_ns['contentAfter'] in self.value_format else ""
				if self.values[-1] == value:
					l_content = self.value_format[ fresnel_ns['contentLast'] ] if fresnel_ns['contentLast'] in self.value_format else l_content
				string += l_content
			string +="</div>\n"
		else:
			string += self.value_format[fresnel_ns['contentNoValue']] if fresnel_ns['contentNoValue'] in self.value_format else ""
		string += "</div>\n"
		
		pl_content = self.property_format[ fresnel_ns['contentAfter'] ] if fresnel_ns['contentAfter'] in self.property_format else ""
		if last:
			if fresnel_ns['contentLast'] in self.property_format:
				pl_content = self.property_format[ fresnel_ns['contentLast'] ]
		string += pl_content
		
		return string

	def renderTable( self ):
		string = ""
		if len( self.values ) > 0 :
			string += "<tr " + renderStyle( self.property_style ) + ">\n"
			if self.label:	
				string += "<td "+ renderStyle( self.label_style ) + ">" + str(self.label).title() + "</td>"
			string += "<td><ul>"
			for value in self.values:
				string += "<li "+ renderStyle( self.value_style ) +">" + value + "</li>\n"
			string += "</ul</td>\n"
			string += "</tr>\n"
		return string

class Sublens:

	def __init__( self, uri, superlens, sublens, lens_uri):
		self.uri = uri
		self.superlens = superlens
		self.sublens = sublens
		self.lens_uri = lens_uri # A BNode which has type propertyDescription
		self.label_style = None
		self.property_style = None
		self.value_style = None

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
		string = "<div id='sublens' " + renderStyle( self.property_style ) +">\n"
		if self.label:
			string += "<div id='label' " + renderStyle( self.label_style ) +">" + self.label + "</div>\n"
		string += "<div id='sublens_value' " + renderStyle( self.value_style ) +">\n" 
		for resource in self.property_set:
			string += resource.render( )
		string += "</div>\n</div>\n"
		return string

	def renderTable( self ):
		string = "<tr " + renderStyle( self.property_style ) + ">\n"
		if self.label:
			string += "<td "+ renderStyle( self.label_style ) +">" + self.label + "</td>\n"
		string += "<td>\n"
		for resource in self.property_set:
			string += resource.render()
		string += "</td>\n</tr>\n"
		return string
