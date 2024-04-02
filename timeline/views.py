import re

import wikipedia
from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse


def fetch_data(request):
    name = request.GET.get('filter[name]', '')

    query = """
        prefix :      <http://127.0.0.1:3333/>
        prefix foaf:  <http://xmlns.com/foaf/0.1/>
        prefix geo:   <http://www.opengis.net/ont/geosparql#>
        prefix owl:   <http://www.w3.org/2002/07/owl#>
        prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
        prefix sem:   <http://semanticweb.cs.vu.nl/2009/11/sem/>
        prefix time:  <http://www.w3.org/2006/time#>
        prefix vcard: <http://www.w3.org/2006/vcard/ns#>
        prefix xsd:   <http://www.w3.org/2001/XMLSchema#>
        select ?baseURI ?event ?label ?pageTitle ?summary ?wikiurl ?image ?dateStart ?dateEnd where {
            ?event rdf:type sem:Event ;
    		       rdfs:label ?label;
    				:summary ?summary;
    				:wikiurl ?wikiurl;
    		OPTIONAL { ?event :image ?image }.

            ?event time:hasTime ?tempEntity .
            ?tempEntity time:hasBeginning ?inst1 ;
                time:hasEnd ?inst2 .

            ?inst1 time:inXSDDate ?dateStart .
            ?inst2 time:inXSDDate ?dateEnd .

            BIND(REPLACE(STR(?event), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI)
            
            FILTER regex(str(?label), "%s", "i") 
             
        }
        """ % name

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []

    # if have no image bisa pake pagetitle buat ambil

    for result in results["results"]["bindings"]:
        data.append({
            "baseURI": result["baseURI"]["value"],
            "event": result["event"]["value"].replace((result["baseURI"]["value"]), ""),
            "summary": re.sub(r'\n', '<br>', result["summary"]["value"]),
            "wikiurl": result["wikiurl"]["value"],
            "image": check_image_availability(result),
            "name": result["label"]["value"],
            "dateStart": result["dateStart"]["value"],
            "dateEnd": result["dateEnd"]["value"],
        })

    return JsonResponse(data, safe=False)

def check_image_availability(result):
    if result.get("image") is None:
        # wikipedia.set_lang("id")
        # page = wikipedia.page(result["pageTitle"]["value"])
        # print(page.images[0])
        return 'Flag_of_Indonesia.svg'
    return result["image"]["value"]


def location(request, name):
    query = """
    prefix :      <http://127.0.0.1:3333/>
    prefix foaf:  <http://xmlns.com/foaf/0.1/> 
    prefix geo:   <http://www.opengis.net/ont/geosparql#> 
    prefix owl:   <http://www.w3.org/2002/07/owl#> 
    prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
    prefix sem:   <http://semanticweb.cs.vu.nl/2009/11/sem/> 
    prefix time:  <http://www.w3.org/2006/time#> 
    prefix vcard: <http://www.w3.org/2006/vcard/ns#> 
    prefix xsd:   <http://www.w3.org/2001/XMLSchema#> 
    
    select ?label ?lat ?lon where {{
        :%s rdf:type sem:Event ;
            rdfs:label ?label ;
            :location ?feature .
        
        ?feature geo:hasGeometry ?geometry .
        ?geometry :latitude ?lat ;
            :longitude ?lon .
    }}
""" % name

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []

    for result in results["results"]["bindings"]:
        data.append({
            "name": name,
            "label": result["label"]["value"],
            "latitude": float(result["lat"]["value"]),
            "longitude": float(result["lon"]["value"]),
        })

    return JsonResponse(data, safe=False)
