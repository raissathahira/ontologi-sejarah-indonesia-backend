import re

from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse
from shapely import wkt
from shapely.geometry import mapping

from map.queries import prefix, get_timeline_actor, get_timeline_event, get_timeline_place, \
    get_timeline_event_homepage, get_timeline_actor_homepage, get_timeline_place_homepage, get_timeline_navbar, \
    get_timeline_navbar_actors, get_timeline_navbar_features, get_types, get_search_events_actor, \
    get_search_events_feature

from map.views import get_largest_bound

graphdb = "http://localhost:7200/repositories/indonesia-history-ontology"

def timeline(request):
    search = request.GET.get('filter[search]', '').replace('(', '\\\(').replace(')', '\\\)')
    role = request.GET.get('filter[role]', '')
    query = prefix

    if role == 'Actor':
        query += get_timeline_actor.format(search)
    elif role == 'Event':
        query += get_timeline_event.format(search)
    elif role == 'Feature':
        query += get_timeline_place.format(search)

    sparql = SPARQLWrapper(graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = mapping_timeline(role, results)

    return JsonResponse(data, safe=False)


def show_events(request):
    iri = request.GET.get('filter[iri]', '')

    query = prefix + get_types.format(iri)

    sparql = SPARQLWrapper(graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    if 'Actor' in  results['results']['bindings'][0]['typeLabels']['value']:
        q2 = prefix + get_search_events_actor.format(iri)
    else :
        q2 = prefix + get_search_events_feature.format(iri)

    sparql = SPARQLWrapper(graphdb)
    sparql.setQuery(q2)
    sparql.setReturnFormat(JSON)

    results2 = sparql.query().convert()
    data = mapping_timeline('Event', results2)

    return JsonResponse(data, safe=False)


def homepage_actor(request):
    query_actor = prefix + get_timeline_actor_homepage

    sparql = SPARQLWrapper(graphdb)
    sparql.setQuery(query_actor)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = mapping_timeline('Actor', results)

    return JsonResponse(data, safe=False)


def homepage_event(request):
    query_event = prefix + get_timeline_event_homepage

    sparql = SPARQLWrapper(graphdb)
    sparql.setQuery(query_event)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = mapping_timeline('Event', results)

    return JsonResponse(data, safe=False)


def homepage_place(request):
    query_place = prefix + get_timeline_place_homepage

    sparql = SPARQLWrapper(graphdb)
    sparql.setQuery(query_place)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = mapping_timeline('Feature', results)

    return JsonResponse(data, safe=False)

def timeline_navbar(request):

    query = prefix + get_timeline_navbar

    sparql = SPARQLWrapper(graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = mapping_timeline('Event', results)

    return JsonResponse(data, safe=False)

def show_actors(request):
    query = prefix + get_timeline_navbar_actors

    sparql = SPARQLWrapper(graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = mapping_timeline('Actor', results)

    return JsonResponse(data, safe=False)

def show_features(request):
    query = prefix + get_timeline_navbar_features

    sparql = SPARQLWrapper(graphdb)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = []
    for result in results["results"]["bindings"]:
        data.append({
            "baseURI": result["baseURI"]["value"],
            "thing": result["thing"]["value"].replace((result["baseURI"]["value"]), ""),
            "summary": result["summary"]["value"] if result.get("summary", {}).get("value") else '',
            "wikiurl": result["wikiurl"]["value"] if result.get("wikiurl", {}).get("value") else '',
            "image": result["image"]["value"] if result.get("image", {}).get(
                "value") else 'No image available.svg',
            "name": result["label"]["value"],
            "dummyDate": '2000-01-01',
            "typeLabel": "Feature"
        })

    return JsonResponse(data, safe=False)

def mapping_timeline(role, results):
    data = []

    if role == 'Event':
        for result in results["results"]["bindings"]:
            data.append({
                "baseURI": result["baseURI"]["value"],
                "thing": result["thing"]["value"].replace((result["baseURI"]["value"]), ""),
                "summary": result["summary"]["value"] if result.get("summary", {}).get("value") else '',
                "wikiurl": result["wikiurl"]["value"] if result.get("wikiurl", {}).get("value") else '',
                "image": result["image"]["value"] if result.get("image", {}).get(
                    "value") else 'No image available.svg',
                "name": result["label"]["value"],
                "firstDateDay": result["firstDateDay"]["value"] if result.get("firstDateDay", {}).get("value") else '',
                "firstDateMonth": result["firstDateMonth"]["value"] if result.get("firstDateMonth", {}).get("value") else '',
                "firstDateYear": result["firstDateYear"]["value"] if result.get("firstDateYear", {}).get("value") else '',
                "secondDateDay": result["secondDateDay"]["value"] if result.get("secondDateDay", {}).get("value") else '',
                "secondDateMonth": result["secondDateMonth"]["value"] if result.get("secondDateMonth", {}).get("value") else '',
                "secondDateYear": result["secondDateYear"]["value"] if result.get("secondDateYear", {}).get("value") else '',
                "typeLabel": "Event"
            })

    elif role == 'Actor':
        for result in results["results"]["bindings"]:
            data.append({
                "baseURI": result["baseURI"]["value"],
                "thing": result["thing"]["value"].replace((result["baseURI"]["value"]), ""),
                "summary": result["summary"]["value"] if result.get("summary", {}).get("value") else '',
                "wikiurl": result["wikiurl"]["value"] if result.get("wikiurl", {}).get("value") else '',
                "image": result["image"]["value"] if result.get("image", {}).get(
                    "value") else 'No image available.svg',
                "name": result["label"]["value"],
                "dummyDate": '2000-01-01',
                "typeLabel": "Actor"
            })

    elif role == 'Feature':
        for result in results["results"]["bindings"]:
            location = [mapping(wkt.loads(result["location"]["value"]))] if "location" in result else None
            data.append({
                "baseURI": result["baseURI"]["value"],
                "thing": result["thing"]["value"].replace((result["baseURI"]["value"]), ""),
                "summary": result["summary"]["value"] if result.get("summary", {}).get("value") else '',
                "wikiurl": result["wikiurl"]["value"] if result.get("wikiurl", {}).get("value") else '',
                "image": result["image"]["value"] if result.get("image", {}).get(
                    "value") else 'No image available.svg',
                "name": result["label"]["value"],
                "latitude": result["latitude"]["value"],
                "longitude": result["longitude"]["value"],
                "location": location,
                "bounds": get_largest_bound(location) if location else None,
                "dummyDate": '2000-01-01',
                "typeLabel": "Feature"
            })

    return data
