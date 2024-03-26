import re

from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse


def fetch_data(request):
    name = request.GET.get('filter[name]', '')

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
        select ?baseURI ?actor ?summary ?wikiurl ?image ?pageTitle ?label ?lat ?lon ?dateStart ?dateEnd where {
            ?actor rdf:type sem:Actor ;
            rdfs:label ?label ;
            :location ?feature ;
            :page_title ?pageTitle ;
            :summary ?summary;
            :wikiurl ?wikiurl;
            OPTIONAL { ?actor :image_map ?image } .
  		    OPTIONAL { ?actor :image_flag ?image } .

            ?feature geo:hasGeometry ?geometry .
            ?geometry :latitude ?lat ;
                :longitude ?lon .

            ?actor time:hasTime ?tempEntity .
            ?tempEntity time:hasBeginning ?inst1 ;
                time:hasEnd ?inst2 .

            ?inst1 time:inXSDDate ?dateStart .
            ?inst2 time:inXSDDate ?dateEnd .

            BIND(REPLACE(STR(?actor), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI)
            
            FILTER regex(str(?label), "%s", "i") 
             
        }
        """ % name

    sparql = SPARQLWrapper("http://localhost:7200/repositories/orde-lama")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []

    for result in results["results"]["bindings"]:
        data.append({
            "baseURI": result["baseURI"]["value"],
            "actor": result["actor"]["value"].replace((result["baseURI"]["value"]), ""),
            "summary": re.sub(r'\n', '<br>', result["summary"]["value"]),
            "wikiurl": result["wikiurl"]["value"],
            "image": result.get("image", {"value": ""})["value"],
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
    
    select ?label ?lat ?lon where {{
        :%s rdf:type sem:Actor ;
            rdfs:label ?label ;
            :location ?feature .
        
        ?feature geo:hasGeometry ?geometry .
        ?geometry :latitude ?lat ;
            :longitude ?lon .
    }}
""" % name

    sparql = SPARQLWrapper("http://localhost:7200/repositories/orde-lama")
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
