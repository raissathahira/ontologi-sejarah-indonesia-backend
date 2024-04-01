from django.shortcuts import render
from rdflib import Graph,Namespace
import requests
from SPARQLWrapper import SPARQLWrapper, JSON,N3,TURTLE,RDFXML,CSV,TSV
from django.http import HttpResponse
import json
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
 
common = "http://commons.wikimedia.org/wiki/Special:FilePath/"
notFound = "default.png"
def fetch_wikidata(params):
    url = 'https://www.wikidata.org/w/api.php'
    return requests.get(url, params=params)
    
def get_image2(name):
    try:
        params = {
            'action': 'wbsearchentities',
            'format': 'json',
            'search': name,
            'language': 'en'
        }
    
        # Fetch API
        data = fetch_wikidata(params)
        
        #show response as JSON
        data = data.json()
        id = data['search'][0]['id']

        params = {
                'action': 'wbgetentities',
                'ids': id,
                'format': 'json',
                'languages': 'en'
            }
        # Fetch API
        data = fetch_wikidata(params)
        
        #show response as JSON
        data = data.json()
        # return JsonResponse(data,safe='false')
        
        image = data['entities'][id]['claims']['P18'][0]["mainsnak"]["datavalue"]['value']
        res = {'image':common + image}
        return common+image
    except:
        return notFound

def get_image(request,name):
    try:
        params = {
            'action': 'wbsearchentities',
            'format': 'json',
            'search': name,
            'language': 'en'
        }
    
        # Fetch API
        data = fetch_wikidata(params)
        
        #show response as JSON
        data = data.json()
        id = data['search'][0]['id']

        params = {
                'action': 'wbgetentities',
                'ids': id,
                'format': 'json',
                'languages': 'en'
            }
        # Fetch API
        data = fetch_wikidata(params)
        
        #show response as JSON
        data = data.json()
        return JsonResponse(data,safe='false')
        
        image = data['entities'][id]['claims']['P18'][0]["mainsnak"]["datavalue"]['value']
        res = {'image':common + image}
        return JsonResponse(res,safe='false')
    except:
        return JsonResponse(notFound,safe='false')


    


blazegraph_url ="http://localhost:7200/repositories/indonesian-history-ontology"

def template(sourcedata,prefix,name):
    if(sourcedata=="internal"):
        source = blazegraph_url
    elif(sourcedata == 'dbpedia'):
        source = "https://dbpedia.org/sparql"
    
    sparql = SPARQLWrapper(
            source
            )
    print(name)
    sparql.setQuery("""
                PREFIX dbo: <http://dbpedia.org/ontology/>
                prefix :    <http://127.0.0.1:3333/> 
                prefix knoprop: <http://knowledge.com/property#> 
                prefix owl:   <http://www.w3.org/2002/07/owl#> 
                prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
                prefix vcard: <http://www.w3.org/2006/vcard/ns#> 
                prefix xsd:   <http://www.w3.org/2001/XMLSchema#>
                prefix resource: <http://dbpedia.org/resource/> 
                prefix sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
                select distinct ?p ?label where{ ?s rdfs:label \""""+name+"""\".
                                              ?s ?p ?o.
                                              ?o rdfs:label ?label.
                                              ?p rdfs:range ?r.
                                              ?r rdfs:subClassOf sem:Core}
                """
            )
    
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    hasil = {}
    # print(ret)
    variable = ret['head']['vars']
    for r in ret["results"]["bindings"]:
        if(hasil.get(clean(r['p']['value']),-1)==-1):
            hasil[clean(r['p']['value'])] = [clean(r['label']['value'])]
        else :
            hasil[clean(r['p']['value'])].append(clean(r['label']['value']))
        
    return hasil

def template2(sourcedata,prefix):
    if(sourcedata=="internal"):
        source = blazegraph_url
    elif(sourcedata == 'dbpedia'):
        source = "https://dbpedia.org/sparql"
    
    sparql = SPARQLWrapper(
            source
            )
    sparql.setQuery("""
                PREFIX dbo: <http://dbpedia.org/ontology/>
                prefix :    <http://127.0.0.1:3333/> 
                prefix knoprop: <http://knowledge.com/property#> 
                prefix owl:   <http://www.w3.org/2002/07/owl#> 
                prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
                prefix vcard: <http://www.w3.org/2006/vcard/ns#> 
                prefix xsd:   <http://www.w3.org/2001/XMLSchema#>
                prefix resource: <http://dbpedia.org/resource/> 
                prefix sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
                select distinct ?s ?label  where{  ?s rdf:type sem:Event.
                                                ?s rdfs:label ?label.}
                """ 
            )
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    hasil = []
    hasil2 = {}
    
                # print(ret)
    variable = ret['head']['vars']
    for r in ret["results"]["bindings"]:
        hasil.append(clean(r['label']['value']))
        hasil2[clean(r['label']['value'])] = clean(r['s']['value'])
        hasil2[clean(r['s']['value'])] = clean(r['label']['value'])

    sparql = SPARQLWrapper(
            source
            )
    sparql.setQuery("""
                PREFIX dbo: <http://dbpedia.org/ontology/>
                prefix :    <http://127.0.0.1:3333/> 
                prefix knoprop: <http://knowledge.com/property#> 
                prefix owl:   <http://www.w3.org/2002/07/owl#> 
                prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
                prefix vcard: <http://www.w3.org/2006/vcard/ns#> 
                prefix xsd:   <http://www.w3.org/2001/XMLSchema#>
                prefix resource: <http://dbpedia.org/resource/> 
                prefix sem: <https://semanticweb.cs.vu.nl/2009/11/sem/>
                select distinct ?s ?label  where{  ?s rdf:type sem:Actor.
                                                ?s rdfs:label ?label.}
                """ 
            )
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    
                # print(ret)
    variable = ret['head']['vars']
    for r in ret["results"]["bindings"]:
        hasil.append(clean(r['label']['value']))
        hasil2[clean(r['label']['value'])] = clean(r['s']['value'])
        hasil2[clean(r['s']['value'])] = clean(r['label']['value'])
        

    return [hasil,hasil2]

def clean(iri):
    # print(iri)
    if(iri[:4]!='http'):
        return iri
    if(iri.find("#") != -1):
        return iri[iri.find('#')+1:]
    else:
        return iri[len(iri)-iri[::-1].find("/"):]
    
@csrf_exempt
def uri_page(request):
    # try:
        data = json.loads(request.body)
        # print("label",data['label'])
        hasil = template("internal",":",data.get("label",""))
        hasil['image'] = get_image2(data.get("label",""))
        print(hasil['image'])
        return JsonResponse(hasil,safe=False)
    # except Exception as e:
def event(request):
    return JsonResponse(template2("internal",":"),safe=False)
         