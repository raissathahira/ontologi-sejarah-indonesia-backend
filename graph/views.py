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
from .queries import *

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
        
        
        image = data['entities'][id]['claims']['P18'][0]["mainsnak"]["datavalue"]['value']
        alias = data['entities'][id]['aliases']['en']
        res = {'image':common + image}
        return JsonResponse(res,safe='false')
    except:
        return JsonResponse({'response':notFound},safe='false')

def get_alias(request,name):
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
        
        
        
        alias = data['entities'][id]['aliases']['en']
        res = {
                'alias':alias}
        return JsonResponse(res,safe='false')
    except:
        return JsonResponse({'response':notFound},safe='false')

    


blazegraph_url ="http://34.87.85.50:7200/repositories/indonesia-history-ontology"

def label(iri):
    query = (prefix + get_label).format(iri)
    sparql = SPARQLWrapper(
            blazegraph_url
            )
    print(iri)
    sparql.setQuery(query
            )
    
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    if ret["results"]["bindings"] == []:
        return ""
    return ret['results']['bindings'][0]['label']['value']
def template(sourcedata,iri):
    if(sourcedata=="internal"):
        source = blazegraph_url
    elif(sourcedata == 'dbpedia'):
        source = "https://dbpedia.org/sparql"
    query = (prefix + get_data).format(iri)
    print(query)
    sparql = SPARQLWrapper(
            source
            )
    print(iri)
    sparql.setQuery(query
            )
    
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    # hasil = {'property': {
    #                         'nama_property':{
    #                                             'value':[{
    #                                                     'iri':
    #                                                     'label':
    #                                                     'detail':
    #                                                     }]
    #                                             'status':
    #                                         }
    #                     }
    #          'image':
    #          'label':}

    # print(ret)
    hasil = {
        'property':{},
        'image':"",
        'label':"",
        'teks':""
    }
    
    if ret["results"]["bindings"] == []:
        return hasil
    variable = ret['head']['vars']
    for r in ret["results"]["bindings"]:
        if(hasil['property'].get(clean(r['p']['value']),-1)==-1):
            hasil['property'][clean(r['p']['value'])] = {'value':[{
                                                                    'iri':clean(r['o']['value']),
                                                                    'label':clean(r['olabel']['value']),
                                                                    'detail':clean(r['comment']['value']),
                                                                    
                                                                }],
                                                         'teks':r['plabel']['value'],
                                                         'status':True
                                                        }
        else :
            hasil['property'][clean(r['p']['value'])]['value'].append({
                                                                    'iri':clean(r['o']['value']),
                                                                    'label':clean(r['olabel']['value']),
                                                                    'detail':clean(r['plabel']['value']),
                                                                    'teks':r['comment']['value']
                                                                })
        
    return hasil


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
        hasil = template("internal",data.get("iri",""))
        hasil['label'] = label(data.get("iri",""))
        hasil['image'] = get_image2(hasil['label'])
        hasil['type']=get_type2(data.get('iri',''))
        hasil['start-year']=get_year(data.get('iri',''),hasil['type'])
        hasil['wikiurl'] = get_wikiurl2(data.get('iri'))
        hasil['type'] = clean(hasil['type'])
        
        print(hasil['image'])
        return JsonResponse(hasil,safe=False)
    # except Exception as e:
def event(request):
    return JsonResponse(template2("internal",":"),safe=False)

def tes(request):
    print(request.headers)
    # print(request.META)
    return JsonResponse({'ok':'ok'})

def get_type2(iri):
    query = (prefix + get_type).format(iri)
    sparql = SPARQLWrapper(
            blazegraph_url
            )
    print(iri)
    sparql.setQuery(query
            )
    
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    if ret["results"]["bindings"] == []:
        return ""
    return ret['results']['bindings'][0]['type']['value']

def get_wikiurl2(iri):
    query = (prefix + get_wikiurl).format(iri)
    sparql = SPARQLWrapper(
            blazegraph_url
            )
    print(iri)
    sparql.setQuery(query
            )
    
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    if ret["results"]["bindings"] == []:
        return ""
    return ret['results']['bindings'][0]['wikiurl']['value']

def get_year(iri,type):
    if(type=="sem:Event"):
        query = (prefix + get_start_year_event).format(iri)
    else:
        query = query = (prefix + get_start_year).format(iri)
    sparql = SPARQLWrapper(
            blazegraph_url
            )
    print(iri)
    sparql.setQuery(query
            )
    
    sparql.setReturnFormat(JSON)
    ret = sparql.queryAndConvert()
    if ret["results"]["bindings"] == []:
        return ""
    return ret['results']['bindings'][0]['year']['value']
         