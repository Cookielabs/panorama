from Selector import *
from Formatter import *
from Fresnel import *
from rdflib import *

def main():

	f = open('data/person_foaf.n3')
	fresnel_data = f.read()
	fresnel = Fresnel( fresnel_data )
	print "Created Fresnel Graph.."
	rdf_graph = Graph()
	print "Downloading resource.."
	f = open('data/Tim_Berners-Lee.rdf')
	rdf_graph.parse( file=f, format="xml")
	for term in rdf_graph:
		print term
	print "Making selection.."
	selector = Selector( fresnel , rdf_graph)
	selector.select()
	formatter = Formatter( selector )
	formatter.format()
	data = "" 
	for resource in formatter.result:
		print resource.render()
		data += resource.render()
	
	f = open('output/test.html', 'w')
	f.write(data.encode('utf-16'))
	

if __name__ == "__main__":
	main()
