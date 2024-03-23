from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse

def fetch_data(request):
    query = """
prefix :      <http://localhost:3333/> 
prefix foaf:  <http://xmlns.com/foaf/0.1/> 
prefix geo:   <http://www.opengis.net/ont/geosparql#> 
prefix owl:   <http://www.w3.org/2002/07/owl#> 
prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
prefix sem:   <http://semanticweb.cs.vu.nl/2009/11/sem/> 
prefix time:  <http://www.w3.org/2006/time#> 
prefix vcard: <http://www.w3.org/2006/vcard/ns#> 
prefix xsd:   <http://www.w3.org/2001/XMLSchema#> 

select ?label ?lat ?lon ?dateStart ?dateEnd where {
    ?actor rdf:type sem:Actor ;
    	rdfs:label ?label ;
    	:location ?feature .
    
    ?feature geo:hasGeometry ?geometry .
    ?geometry :latitude ?lat ;
    	:longitude ?lon .
    
    ?actor time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
    	time:hasEnd ?inst2 .
    
    ?inst1 time:inXSDDate ?dateStart .
    ?inst2 time:inXSDDate ?dateEnd .
}
"""

    sparql = SPARQLWrapper("http://localhost:7200/repositories/orde-lama")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []

    for result in results["results"]["bindings"]:
        data.append({
            "name": result["label"]["value"],
            "dateStart": result["dateStart"]["value"],
            "dateEnd": result["dateEnd"]["value"],
            "latitude": float(result["lat"]["value"]),
            "longitude": float(result["lon"]["value"]),
        })

    return JsonResponse(data, safe=False)

def location(request, name):
    query = """
prefix :      <http://localhost:3333/> 
prefix foaf:  <http://xmlns.com/foaf/0.1/> 
prefix geo:   <http://www.opengis.net/ont/geosparql#> 
prefix owl:   <http://www.w3.org/2002/07/owl#> 
prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
prefix sem:   <http://semanticweb.cs.vu.nl/2009/11/sem/> 
prefix time:  <http://www.w3.org/2006/time#> 
prefix vcard: <http://www.w3.org/2006/vcard/ns#> 
prefix xsd:   <http://www.w3.org/2001/XMLSchema#> 

select ?label ?lat ?lon ?dateStart ?dateEnd where {{
    ?actor rdf:type sem:Actor ;
    	rdfs:label '%s' ;
    	:location ?feature .
    
    ?feature geo:hasGeometry ?geometry .
    ?geometry :latitude ?lat ;
    	:longitude ?lon .
    	
    ?actor time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
    	time:hasEnd ?inst2 .
    
    ?inst1 time:inXSDDate ?dateStart .
    ?inst2 time:inXSDDate ?dateEnd .
}}
""" %(name)

    sparql = SPARQLWrapper("http://localhost:7200/repositories/orde-lama")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []

    for result in results["results"]["bindings"]:
        data.append({
            "name": name,
            "dateStart": int(result["dateStart"]["value"][0:4]),
            "dateEnd": int(result["dateEnd"]["value"][0:4]),
            "latitude": float(result["lat"]["value"]),
            "longitude": float(result["lon"]["value"]),
        })

    return JsonResponse(data, safe=False)
