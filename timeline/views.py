import re

from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse

from map.queries import prefix, get_timeline, get_all, get_search_events


def timeline(request):
    search = request.GET.get('filter[search]', '')
    role = request.GET.get('filter[role]', '')

    query = prefix + get_timeline.format(role, search)

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []

    for result in results["results"]["bindings"]:
        data.append({
            "baseURI": result["baseURI"]["value"],
            "thing": result["thing"]["value"].replace((result["baseURI"]["value"]), ""),
            "summary": re.sub(r'\n', '<br>', result["summary"]["value"]),
            "wikiurl": result["wikiurl"]["value"],
            "image": check_image_availability(result),
            "name": result["label"]["value"],
            "firstDate": result["firstDate"]["value"],
            "secondDate": result["secondDate"]["value"],
        })

    return JsonResponse(data, safe=False)


def show_events(request):
    iri = request.GET.get('filter[iri]', '')

    query = prefix + get_search_events.format(iri)

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []

    for result in results["results"]["bindings"]:
        data.append({
            "baseURI": result["baseURI"]["value"],
            "event": result["event"]["value"].replace((result["baseURI"]["value"]), ""),
            "summary": re.sub(r'\n', '<br>', result["summary"]["value"]),
            "wikiurl": result["wikiurl"]["value"],
            "image": check_image_availability(result),
            "name": result["label"]["value"],
            "firstDate": result["firstDate"]["value"],
            "secondDate": result["secondDate"]["value"],
            "actorLabel": result["actorLabel"]["value"]
        })

    return JsonResponse(data, safe=False)


def check_image_availability(result):
    if result.get("image") is None:
        return 'Indonesia flag raising witnesses 17 August 1945.jpg'
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
    prefix dc:    <http://purl.org/dc/elements/1.1/>
    
    PREFIX local: <http://127.0.0.1:3333/>
    SELECT DISTINCT ?baseURI ?person ?label ?summary ?wikiurl ?image ?birthDate ?deathDate WHERE {
      ?person rdf:type :Person ;
             rdfs:label ?label ;
             ?predicate ?summary .
      FILTER(?predicate IN (:summary, dc:description))  
    
      OPTIONAL { 
        ?event :image ?image .
        {
          SELECT ?person (SAMPLE(?image) AS ?image) WHERE {
            ?person rdf:type :Person ;
                   rdfs:label ?label ;
                   ?predicate ?summary .
            FILTER(?predicate IN (:summary, dc:description))
            OPTIONAL { ?event :image ?image }.
          } GROUP BY ?person
        }
      }
    
      OPTIONAL { ?event :wikiurl ?wikiurl }
    
      ?person time:hasTime ?tempEntity .
      ?tempEntity time:hasBeginning ?inst1 ;
                  time:hasEnd ?inst2 .
    
      ?inst1 time:inXSDDate ?birthDate .
      ?inst2 time:inXSDDate ?deathDate .
    
      BIND(REPLACE(STR(?event), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI)
      
      FILTER regex(str(?label), "%s", "i") 
    } ORDER BY ?person
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
            "person": result["person"]["value"].replace((result["baseURI"]["value"]), ""),
            "summary": re.sub(r'\n', '<br>', result["summary"]["value"]),
            "wikiurl": result["wikiurl"]["value"],
            "image": check_image_availability(result),
            "name": result["label"]["value"],
            "birthDate": result["birthDate"]["value"],
            "deathDate": result["deathDate"]["value"],
        })

    return JsonResponse(data, safe=False)
