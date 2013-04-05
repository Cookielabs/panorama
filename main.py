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
	#rdf_graph.parse(source="http://dbpedia.org/page/A._P._J._Abdul_Kalam")
	print "more..."
	
	f = open('data/A._P._J._Abdul_Kalam.rdf')
	rdf_graph.parse( file=f, format="xml")
	#rdf_graph.parse(source="http://dbpedia.org/page/Tim_Berners-Lee")
	for term in rdf_graph:
		print term
	print "Making selection.."
	selector = Selector( fresnel , rdf_graph)
	selector.select()
	formatter = Formatter( selector )
	formatter.format()
	data = "<html>\n<head><link rel='stylesheet' type='text/css' href='style.css'></head>\n<body>\n" 
	for resource in formatter.result:
		print resource.render()
		data += resource.render()
	data += "</body>\n</html>"
	f = open('output/test.html', 'w')
	f.write(data.encode('utf-8'))
	

if __name__ == "__main__":
	main()
