import re

from SPARQLWrapper import SPARQLWrapper, JSON
from django.http import JsonResponse

from map.queries import prefix, get_timeline_actor, get_timeline_event, get_timeline_place, get_search_events


def timeline(request):
    global query
    search = request.GET.get('filter[search]', '')
    role = request.GET.get('filter[role]', '')

    if role == 'Actor':
        query = prefix + get_timeline_actor.format(search)
    elif role == 'Event':
        query = prefix + get_timeline_event.format(search)
    elif role == 'Place':
        query = prefix + get_timeline_place.format(search)

    sparql = SPARQLWrapper("http://localhost:7200/repositories/indonesian-history-ontology")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    data = mapping_timeline(role, results)

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
            "image": result["image"]["value"] if result.get("image", {}).get("value") else 'Indonesia flag raising witnesses 17 August 1945.jpg',
            "name": result["label"]["value"],
            "firstDate": result["firstDate"]["value"],
            "secondDate": result["secondDate"]["value"],
            "actorLabel": result["actorLabel"]["value"]
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
                "image": result["image"]["value"] if result.get("image", {}).get("value") else 'Indonesia flag raising witnesses 17 August 1945.jpg',
                "name": result["label"]["value"],
                "firstDate": result["firstDate"]["value"],
                "secondDate": result["secondDate"]["value"],
            })

    elif role == 'Actor':
        for result in results["results"]["bindings"]:
            data.append({
                "baseURI": result["baseURI"]["value"],
                "thing": result["thing"]["value"].replace((result["baseURI"]["value"]), ""),
                "summary": result["summary"]["value"] if result.get("summary", {}).get("value") else '',
                "wikiurl": result["wikiurl"]["value"] if result.get("wikiurl", {}).get("value") else '',
                "image": result["image"]["value"] if result.get("image", {}).get("value") else 'Indonesia flag raising witnesses 17 August 1945.jpg',
                "name": result["label"]["value"],
                "dummyDate": '2000-01-01',
            })

    elif role == 'Place':
        for result in results["results"]["bindings"]:
            data.append({
                "baseURI": result["baseURI"]["value"],
                "thing": result["thing"]["value"].replace((result["baseURI"]["value"]), ""),
                "summary": result["summary"]["value"] if result.get("summary", {}).get("value") else '',
                "wikiurl": result["wikiurl"]["value"] if result.get("wikiurl", {}).get("value") else '',
                "image": result["image"]["value"] if result.get("image", {}).get("value") else 'Indonesia flag raising witnesses 17 August 1945.jpg',
                "name": result["label"]["value"],
                "latitude": result["latitude"]["value"],
                "longitude": result["longitude"]["value"],
                "dummyDate": '2000-01-01',
            })

    return data
