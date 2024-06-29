from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse
from shapely import wkt
from shapely.geometry import mapping, shape
from shapely.ops import unary_union
from .queries import prefix, get_map, get_all, get_search, get_total_search, get_types, event, actor, person, place

base_prefix = "http://127.0.0.1:3333/"
graphdb = "http://localhost:7200/repositories/indonesia-history-ontology"

def fetch_map_data(request):
    query = prefix + get_map

    sparql = SPARQLWrapper(
        graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = {}

    for result in results["results"]["bindings"]:
        latitude = float(result["lat"]["value"])
        longitude = float(result["lon"]["value"])

        if latitude not in data:
            data[latitude] = {}

        if longitude not in data[latitude]:
            data[latitude][longitude] = []

        data[latitude][longitude].append({
            "iri": result["event"]["value"][len(base_prefix):],
            "name": result["label"]["value"],
            "yearStart": int(result["yearStart"]["value"]),
        })

    return JsonResponse(data, safe=False)


def fetch_all_data(request):
    query = prefix + get_all

    sparql = SPARQLWrapper(
        graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []

    for result in results["results"]["bindings"]:
        data.append({
            "iri": result["a"]["value"][len(base_prefix):],
            "name": result["label"]["value"],
            "type": result["type"]["value"]
        })

    return JsonResponse(data, safe=False)


def fetch_search_data(request, search, page):
    query = (prefix + get_search).format(search, page)

    sparql = SPARQLWrapper(
        graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []

    for result in results["results"]["bindings"]:
        data.append({
            "iri": result["a"]["value"][len(base_prefix):],
            "name": result["label"]["value"],
            "type": result["type"]["value"],
            "summary": result.get("summary", {}).get("value", ""),
            "firstDateYear": result["firstDateYear"]["value"] if result.get("firstDateYear", {}).get("value") else ''
        })

    return JsonResponse(data, safe=False)


def fetch_total_search(request, search):
    query = (prefix + get_total_search).format(search)

    sparql = SPARQLWrapper(
        graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    result = sparql.query().convert()['results']['bindings'][0]

    data = {'total': result['count']['value']}

    return JsonResponse(data, safe=False)


def get_detail(request, iri):
    type_func = {
        "Event": get_event_detail,
        "Actor": get_actor_detail,
        "Feature": get_place_detail,
        "Person": get_person_detail,
    }

    query = (prefix + get_types).format(iri)

    sparql = SPARQLWrapper(
        graphdb)
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

    sparql = SPARQLWrapper(
        graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"][0]

    if result == []:
        return

    detail["detail"]["name"] = ("Nama", result["label"]["value"])
    detail["wikiurl"] = result["wikiurl"]["value"] if "wikiurl" in result else None
    detail["type"] = "Event"
    
    if "summary" in result:
        detail["detail"]["summary"] = ("Deskripsi", result["summary"]["value"])
    
    startDate = format_date(
        result["dayStart"]["value"] if "dayStart" in result else None,
        result["monthStart"]["value"] if "monthStart" in result else None,
        result["yearStart"]["value"] if "yearStart" in result else None
    )
    
    if startDate is not None:
        detail["detail"]["dateStart"] = (
            "Tanggal mulai", startDate
        )
        
    endDate = format_date(
        result["dayEnd"]["value"] if "dayEnd" in result else None,
        result["monthEnd"]["value"] if "monthEnd" in result else None,
        result["yearEnd"]["value"] if "yearEnd" in result else None
    )
    
    if endDate is not None:
        detail["detail"]["dateEnd"] = (
            "Tanggal selesai", format_date(
                result["dayEnd"]["value"] if "dayEnd" in result else None,
                result["monthEnd"]["value"] if "monthEnd" in result else None,
                result["yearEnd"]["value"] if "yearEnd" in result else None
            )
        )

    multivalued_attr = ["actor", "person", "feature"]
    multivalued_label = ["Pihak terlibat", "Tokoh terlibat", "Lokasi kejadian"]
    
    for i in range(len(multivalued_attr)):
        if result[multivalued_attr[i]]['value']:
            detail["detail"][multivalued_attr[i]] = (multivalued_label[i], [
                (iri[len(base_prefix):], label)
                for iri, label in zip(result[multivalued_attr[i]]["value"].split(","), result[multivalued_attr[i] + "Label"]["value"].split(","))
            ])
        else:
            detail["detail"][multivalued_attr[i]] = (
                multivalued_label[i], None)

    if "location" in result:
        detail["location"] = [
            mapping(wkt.loads(location)) for location in result["location"]["value"].split("|")]
        detail["bounds"] = get_largest_bound(detail["location"])


def get_place_detail(iri, detail):
    query = (prefix + place).format(iri)

    sparql = SPARQLWrapper(
        graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"]

    if result == []:
        return

    detail["wikiurl"] = result["wikiurl"]["value"] if "wikiurl" in result else None
    detail["detail"]["name"] = ("Nama", result[0]["label"]["value"])
    detail["type"] = ["Feature"]
    
    if "summary" in result:
        detail["detail"]["summary"] = ("Deskripsi", result["summary"]["value"])

    detail["detail"]["coordinate"] = (
        "Koordinat (dalam lat dan lng)", "(" + result[0]["lat"]["value"] + ", " + result[0]["lng"]["value"] + ")")

    detail["detail"]["eventOccurred"] = ("Daftar peristiwa", [
        (res["event"]["value"][len(base_prefix):], res["eventLabel"]["value"])
        for res in result
    ])

    detail["location"] = [
        mapping(wkt.loads(res["location"]["value"])) for res in result]
    detail["bounds"] = get_largest_bound(detail["location"])


def get_actor_detail(iri, detail):
    query = (prefix + actor).format(iri)

    sparql = SPARQLWrapper(
        graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"][0]

    detail["image"] = result["image"]["value"] if "image" in result else None
    detail["wikiurl"] = result["wikiurl"]["value"] if "wikiurl" in result else None
    detail["type"] = ["Actor"]
    detail["detail"]["name"] = ("Nama", result["label"]["value"])
    
    if "summary" in result:
        detail["detail"]["summary"] = ("Deskripsi", result["summary"]["value"])
    
    startDate = format_date(
        result["dayStart"]["value"] if "dayStart" in result else None,
        result["monthStart"]["value"] if "monthStart" in result else None,
        result["yearStart"]["value"] if "yearStart" in result else None
    )
    
    if startDate is not None:
        detail["detail"]["dateStart"] = (
            "Tanggal berdiri", startDate
        )
        
    endDate = format_date(
        result["dayEnd"]["value"] if "dayEnd" in result else None,
        result["monthEnd"]["value"] if "monthEnd" in result else None,
        result["yearEnd"]["value"] if "yearEnd" in result else None
    )
    
    if endDate is not None:
        detail["detail"]["dateEnd"] = (
            "Tanggal berakhir", format_date(
                result["dayEnd"]["value"] if "dayEnd" in result else None,
                result["monthEnd"]["value"] if "monthEnd" in result else None,
                result["yearEnd"]["value"] if "yearEnd" in result else None
            )
        )
        
    multivalued_attr = ["event"]
    multivalued_label = ["Terlibat dalam"]
    
    for i in range(len(multivalued_attr)):
        if result[multivalued_attr[i]]['value']:
            detail["detail"][multivalued_attr[i]] = (multivalued_label[i], [
                (iri[len(base_prefix):], label)
                for iri, label in zip(result[multivalued_attr[i]]["value"].split(","), result[multivalued_attr[i] + "Label"]["value"].split(","))
            ])
            
def get_person_detail(iri, detail):
    query = (prefix + person).format(iri)

    sparql = SPARQLWrapper(
        graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"][0]
    
    if "dateStart" in detail["detail"]:
        detail["detail"]["dateStart"] = ("Tanggal lahir", detail["detail"]["dateStart"][1])
        
    if "dateEnd" in detail["detail"]:
        detail["detail"]["dateEnd"] = ("Tanggal kematian", detail["detail"]["dateEnd"][1])
    
    
    multivalued_attr = ["parents", "children", "relative"]
    multivalued_label = ["Orang tua", "Anak", "Kerabat"]
    
    for i in range(len(multivalued_attr)):
        if result[multivalued_attr[i]]['value']:
            detail["detail"][multivalued_attr[i]] = (multivalued_label[i], [
                (iri[len(base_prefix):], label)
                for iri, label in zip(result[multivalued_attr[i]]["value"].split(","), result[multivalued_attr[i] + "Label"]["value"].split(","))
            ])

def format_date(day, month, year):
    if year is None:
        return None
    
    date = ""
    
    if day is not None:
        date += str(day) + " "
    
    month = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }.get(int(month) if month is not None else None, None)
    
    if month is not None:
        date += month + " "

    return date + str(year)
