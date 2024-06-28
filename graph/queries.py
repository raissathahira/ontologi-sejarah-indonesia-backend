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
prefix dc:    <http://purl.org/dc/elements/1.1/>
"""
get_data = """
select DISTINCT ?p ?o ?olabel ?plabel where {{
    :{0} ?p ?o .
    ?p rdfs:range ?type.
    ?o rdfs:label ?olabel .
    ?p rdfs:label ?plabel.
    ?FILTER(?type IN (sem:Actor, sem:Event,geo:Feature,sem:View,foaf:Person))
}}"""

get_label ="""
select DISTINCT ?label where {{
    :{0} rdfs:label ?label
   
}}"""
