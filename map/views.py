from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse
from shapely import wkt
from shapely.geometry import mapping, shape
from .queries import military_conflict

prefix = """
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
"""

def fetch_data(request):
    query = prefix + """
    
select DISTINCT ?event ?label ?lat ?lon ?dateStart ?dateEnd where {
    ?event rdf:type sem:Event ;
    	rdfs:label ?label ;
    	:location ?feature .
    
    ?feature geo:hasGeometry ?geometry .
    ?geometry :latitude ?lat ;
    	:longitude ?lon .
    
    ?event time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
    	time:hasEnd ?inst2 .
    
    ?inst1 time:inXSDDate ?dateStart .
    ?inst2 time:inXSDDate ?dateEnd .
}
"""

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    
    data = []
    
    base_prefix = "http://127.0.0.1:3333/"
    
    for result in results["results"]["bindings"]:
        data.append({
            "iri": result["event"]["value"][len(base_prefix):],
            "name": result["label"]["value"],
            "yearStart": int(result["dateStart"]["value"][-4:]),
            "yearEnd": int(result["dateEnd"]["value"][-4:]),
            "latitude": float(result["lat"]["value"]),
            "longitude": float(result["lon"]["value"]),
        })
    
    return JsonResponse(data, safe=False)


def get_detail(request, iri):
    query = (prefix + military_conflict).format(iri)

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"][0]
    geojson = mapping(wkt.loads(result["location"]["value"])) if "location" in result else None
    
    detail = get_military_conflict_detail(result)
        
    data = {
        "name": result["label"]["value"],
        "geojson": geojson,
        "bounds": get_bound(geojson),
        "detail": detail
    }
    
    return JsonResponse(data, safe=False)

def get_bound(geojson):
    if geojson is None:
        return None
    
    bounds = shape(geojson).bounds
    
    return [
        [bounds[1], bounds[0]],
        [bounds[3], bounds[2]]
    ]
    
def get_military_conflict_detail(result):
    keys = ["label", "result", "combatants1", "combatants2", "commanders1", "commanders2", "strength1", 
            "strength2", "casualties1", "casualties2", "dateStart", "dateEnd"]
    return {key: result[key]["value"] if key in result else None for key in keys}


