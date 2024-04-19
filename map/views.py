from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse
from shapely import wkt
from shapely.geometry import mapping, shape
from shapely.ops import unary_union
from .queries import prefix, get_map, get_all, get_search, get_total_search, get_types, event, actor, place, conflict, military_person

base_prefix = "http://127.0.0.1:3333/"


def fetch_map_data(request):
    query = prefix + get_map

    sparql = SPARQLWrapper(
        "http://localhost:7200/repositories/indonesian-history-ontology")
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
            "yearStart": int(result["dateStart"]["value"][:4]),
            "yearEnd": int(result["dateEnd"]["value"][:4])
        })

    return JsonResponse(data, safe=False)


def fetch_all_data(request):
    query = prefix + get_all

    sparql = SPARQLWrapper(
        "http://localhost:7200/repositories/indonesian-history-ontology")
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
        "http://localhost:7200/repositories/indonesian-history-ontology")
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


def fetch_total_search(request, search):
    query = (prefix + get_total_search).format(search)

    sparql = SPARQLWrapper(
        "http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    result = sparql.query().convert()['results']['bindings'][0]

    data = {'total': result['count']['value']}

    return JsonResponse(data, safe=False)


def get_detail(request, iri):
    type_func = {
        "Event": get_event_detail,
        "Conflict": get_conflict_detail,
        "Military Person": get_military_person_detail,
        "Actor": get_actor_detail,
        "Feature": get_place_detail
    }

    query = (prefix + get_types).format(iri)

    sparql = SPARQLWrapper(
        "http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"][0]

    types = result["typeLabels"]["value"].split(",")

    print(types)

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
        "http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"]

    if result == []:
        return

    detail["detail"]["name"] = ("Nama", result[0]["label"]["value"])
    detail["detail"]["dateStart"] = (
        "Tanggal mulai", format_date(result[0]["dateStart"]["value"]))
    detail["detail"]["dateEnd"] = (
        "Tanggal selesai", format_date(result[0]["dateEnd"]["value"]))

    detail["detail"]["feature"] = ("Tempat kejadian", [
        (res["feature"]["value"][len(base_prefix):], res["featureLabel"]["value"])
        for res in result
    ])

    if "location" in result[0]:
        detail["location"] = [
            mapping(wkt.loads(res["location"]["value"])) for res in result]
        detail["bounds"] = get_largest_bound(detail["location"])


def get_place_detail(iri, detail):
    query = (prefix + place).format(iri)

    print(query)

    sparql = SPARQLWrapper(
        "http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"]

    if result == []:
        return

    detail["detail"]["name"] = ("Nama", result[0]["label"]["value"])

    detail["detail"]["coordinate"] = (
        "Koordinat (dalam lat dan lng)", "(" + result[0]["lat"]["value"] + ", " + result[0]["lng"]["value"] + ")")

    detail["detail"]["event"] = ("Daftar peristiwa", [
        (res["event"]["value"][len(base_prefix):], res["eventLabel"]["value"])
        for res in result
    ])

    detail["location"] = [
        mapping(wkt.loads(res["location"]["value"])) for res in result]
    detail["bounds"] = get_largest_bound(detail["location"])


def get_actor_detail(iri, detail):
    query = (prefix + actor).format(iri)

    sparql = SPARQLWrapper(
        "http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"]

    detail["detail"]["name"] = ("Nama", result[0]["label"]["value"])
    if ("dateStart" in result[0]):
        detail["detail"]["dateStart"] = (
            "Tanggal mulai", result[0]["dateStart"]["value"])
    if ("dateEnd" in result[0]):
        detail["detail"]["dateEnd"] = (
            "Tanggal selesai", result[0]["dateEnd"]["value"])


def get_conflict_detail(iri, detail):
    query = (prefix + conflict).format(iri)

    sparql = SPARQLWrapper(
        "http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"][0]

    multivalued_attr = ["side", "leadfigure"]
    multivalued_label = ["Pihak terlibat", "Pemimpin pihak terlibat"]

    for i in range(len(multivalued_attr)):
        if result[multivalued_attr[i]]['value']:
            detail["detail"][multivalued_attr[i]] = (multivalued_label[i], [
                (iri[len(base_prefix):], label)
                for iri, label in zip(result[multivalued_attr[i]]["value"].split(","), result[multivalued_attr[i] + "Label"]["value"].split(","))
            ])
        else:
            detail["detail"][multivalued_attr[i]] = (
                multivalued_label[i], None)

    detail["detail"]["casualties"] = (
        "Korban", result["casualties"]["value"] if "casualties" in result else None)
    detail["detail"]["causes"] = (
        "Penyebab", result["causes"]["value"] if "causes" in result else None)


def get_military_person_detail(iri, detail):
    query = (prefix + military_person).format(iri)
    print(query)
    sparql = SPARQLWrapper(
        "http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    result = results["results"]["bindings"][0]

    multivalued_attr = ["commands", "children", "battles", 'spouse']
    multivalued_label = ["pasukan", "anak", "Pertempuran", 'pasangan']

    for i in range(len(multivalued_attr)):
        if multivalued_attr[i] in result:
            detail["detail"][multivalued_attr[i]] = (multivalued_label[i], [
                (iri[len(base_prefix):], label)
                for iri, label in zip(result[multivalued_attr[i]]["value"].split(","), result[multivalued_attr[i] + "Label"]["value"].split(","))
            ])
    print(result)
    detail["detail"]["name"] = ("Nama", result["label"]["value"])
    detail["detail"]["religion"] = (
        "Agama", result["religion"]["value"] if "religion" in result else None)
    detail["detail"]["laterwork"] = (
        "Karya", result["laterwork"]["value"] if "laterwork" in result else None)
    detail["detail"]["birthname"] = (
        "nama lahir", result["birthname"]["value"] if "birthname" in result else None)
    detail["detail"]["awards"] = (
        "Penghargaan", result["awards"]["value"] if "awards" in result else None)
    # detail["detail"]["casualties2"] = ("Korban pihak 2", result["casualties2"]["value"] if "casualties2" in result else None)
    # detail["detail"]["causes"] = ("Penyebab", result["causes"]["value"] if "causes" in result else None)

def format_date(date):
    year, month, day = map(int, date.split("-"))

    months = {
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
    }
    
    return f"{day} {months.get(month)} {year}"