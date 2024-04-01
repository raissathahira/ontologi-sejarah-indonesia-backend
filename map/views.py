from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse
from shapely import wkt
from shapely.geometry import mapping, shape
from shapely.ops import unary_union
from .queries import prefix, get_map, get_all, get_types, event, military_conflict

base_prefix = "http://127.0.0.1:3333/"

def fetch_map_data(request):
    query = prefix + get_map

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    
    data = []
    
    for result in results["results"]["bindings"]:
        data.append({
            "iri": result["event"]["value"][len(base_prefix):],
            "name": result["label"]["value"],
            "yearStart": int(result["dateStart"]["value"][:4]),
            "yearEnd": int(result["dateEnd"]["value"][:4]),
            "latitude": float(result["lat"]["value"]),
            "longitude": float(result["lon"]["value"]),
        })
    
    return JsonResponse(data, safe=False)

def fetch_all_data(request):
    query = prefix + get_all

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    
    data = []
    
    for result in results["results"]["bindings"]:
        data.append({
            "iri": result["a"]["value"][len(base_prefix):],
            "name": result["label"]["value"]
        })
    
    return JsonResponse(data, safe=False)


def get_detail(request, iri):
    type_func = {
        "Event": get_event_detail,
        "Military Conflict": get_military_conflict_detail
    }
    
    query = (prefix + get_types).format(iri)

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"][0]
    
    types = result["typeLabels"]["value"].split(",")
    
    detail = {}
    detail["detail"] = {}
    
    for type_, func in type_func.items():
        if type_ in types:
            func(iri, detail)
    
    return JsonResponse(detail, safe=False)

def get_largest_bound(geojson_list):
    if geojson_list is None:
        return None
    
    shapes = [shape(geojson) for geojson in geojson_list]
    
    multi_poly = unary_union(shapes)
    
    bounds = shape(multi_poly).bounds
    
    return [
        [bounds[1], bounds[0]],
        [bounds[3], bounds[2]]
    ]
    
def get_event_detail(iri, detail):
    query = (prefix + event).format(iri)

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"]
    
    detail["detail"]["name"] = ("Nama", result[0]["label"]["value"])
    detail["detail"]["dateStart"] = ("Tanggal mulai", result[0]["dateStart"]["value"])
    detail["detail"]["dateEnd"] = ("Tanggal selesai", result[0]["dateEnd"]["value"])
    
    
    detail["detail"]["feature"] = ("Tempat kejadian", [
        (res["feature"]["value"][len(base_prefix):], res["featureLabel"]["value"])
        for res in result
    ])

    if "location" in result[0]:
        detail["location"] = [mapping(wkt.loads(res["location"]["value"])) for res in result]
        detail["bounds"] = get_largest_bound(detail["location"])
    
def get_military_conflict_detail(iri, detail):
    query = (prefix + military_conflict).format(iri)
    
    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"][0]
    
    multivalued_attr = ["combatants1", "combatants2", "commanders1", "commanders2"]
    multivalued_label = ["Pihak 1", "Pihak 2", "Pemimpin pihak 1", "Pemimpin pihak 2"]

    for i in range(len(multivalued_attr)):
        if multivalued_attr[i] in result:
            detail["detail"][multivalued_attr[i]] = (multivalued_label[i], [
                (iri[len(base_prefix):], label)
                for iri, label in zip(result[multivalued_attr[i]]["value"].split(","), result[multivalued_attr[i] + "Label"]["value"].split(","))
            ])

    detail["detail"]["strength1"] = ("Kekuatan pihak 1", result["strength1"]["value"] if "strength1" in result else None)
    detail["detail"]["strength2"] = ("Kekuatan pihak 2", result["strength2"]["value"] if "strength2" in result else None)
    detail["detail"]["casualties1"] = ("Korban pihak 1", result["casualties1"]["value"] if "casualties1" in result else None)
    detail["detail"]["casualties2"] = ("Korban pihak 2", result["casualties2"]["value"] if "casualties2" in result else None)
    detail["detail"]["causes"] = ("Penyebab", result["causes"]["value"] if "causes" in result else None)
