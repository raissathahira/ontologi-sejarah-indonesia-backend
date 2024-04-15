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

get_all = """
select DISTINCT ?a ?label ?type where {
    ?a rdf:type ?type ;
    rdfs:label ?label .
    FILTER (?type IN ( sem:Event, sem:Actor, sem:Place ))
}"""

get_search = """
select DISTINCT ?a ?label where {{
    ?a rdf:type ?type ;
        rdfs:label ?label ;
        ?b ?c .
    FILTER (?type IN ( sem:Event, sem:Actor, sem:Place ))
    FILTER (CONTAINS(LCASE(STR(?c)), LCASE("{0}")))
}}"""

get_map = """ 
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

get_types = """
select DISTINCT 
(GROUP_CONCAT(distinct ?typeLabel; SEPARATOR=",") as ?typeLabels)
where {{
    <http://127.0.0.1:3333/{0}> rdf:type ?type .
    ?type rdfs:label ?typeLabel .
}}
"""

get_timeline_event = """
SELECT DISTINCT  ?baseURI ?thing ?label ?summary ?wikiurl ?image ?firstDate ?secondDate WHERE {{
    ?thing rdf:type	sem:Event ;
    rdfs:label ?label;
    OPTIONAL{{ 
      ?thing :image ?image .
      ?thing :wikiurl ?wikiurl .
      ?thing ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.

      ?thing time:hasTime ?tempEntity .
      ?tempEntity time:hasBeginning ?inst1 ;
                  time:hasEnd ?inst2 .

      ?inst1 time:inXSDDate ?firstDate .
      ?inst2 time:inXSDDate ?secondDate .
      
      BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .
      FILTER regex(str(?label), "{0}", "i") .

    }} ORDER BY ?thing
"""

get_timeline_actor = """
SELECT DISTINCT  ?baseURI ?thing ?label ?summary ?wikiurl ?image WHERE {{
    ?thing rdf:type	:Person ;
    rdfs:label ?label;
    
    OPTIONAL{{ 
      ?thing :image ?image .
      ?thing :wikiurl ?wikiurl .
      ?thing ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.

    BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .
    FILTER regex(str(?label), "{0}", "i") .

    }} ORDER BY ?thing
"""

get_timeline_place = """
SELECT DISTINCT  ?baseURI ?thing ?label ?latitude ?longitude ?summary ?wikiurl ?image WHERE {{
    ?thing rdf:type	geo:Feature ;
    rdfs:label ?label;
    
    OPTIONAL{{ 
      ?thing :image ?image .
      ?thing :wikiurl ?wikiurl .
      ?thing ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.
    
    ?thing geo:hasGeometry ?geometry .
    ?geometry :latitude ?latitude;
        :longitude ?longitude.

    BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .
    FILTER regex(str(?label), "{0}", "i") .

    }} ORDER BY ?thing
"""

get_search_events = """
select DISTINCT ?baseURI ?event ?label ?summary ?wikiurl ?image ?firstDate (SAMPLE(?secondDate) as ?secondDate) ?actorLabel where {{
    ?event rdf:type sem:Event ;
        rdfs:label ?label ;
        :wikiurl ?wikiurl;
        ?predicate ?summary;
    	FILTER(?predicate IN (:summary, dc:description)).
    OPTIONAL{{ ?event :image ?image }}.
        
    ?event ?b ?c .
    
    FILTER (CONTAINS(LCASE(STR(?c)), LCASE("{0}")))
    
    ?event time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
                  time:hasEnd ?inst2 .

      ?inst1 time:inXSDDate ?firstDate .
      ?inst2 time:inXSDDate ?secondDate .
      
      BIND(REPLACE(STR(?event), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI)  
      
    :{0} rdfs:label ?actorLabel  
}} GROUP BY ?baseURI ?event ?label ?summary ?wikiurl ?firstDate ?image ?actorLabel
"""

event = """
select DISTINCT ?label ?dateStart ?dateEnd ?location ?feature ?featureLabel

where {{
    :{0} rdfs:label ?label ;
        :location ?feature .
        
    :{0} time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
    	time:hasEnd ?inst2 .
    
    ?inst1 time:inXSDDate ?dateStart .
    ?inst2 time:inXSDDate ?dateEnd .
    
    ?feature rdfs:label ?featureLabel
    
    OPTIONAL {{ 
        ?feature geo:hasGeometry ?geometry .
    
        ?geometry geo:asWKT ?location .
    }}
}}
"""

actor = """
select DISTINCT ?label ?dateStart ?dateEnd

where {{
    :{0} rdfs:label ?label .
        
        
    :{0} time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
    	time:hasEnd ?inst2 .
    optional {{
    ?inst1 time:inXSDDate ?dateStart .
    }}
    optional {{
    ?inst2 time:inXSDDate ?dateEnd .
    }}
    
    
}}
"""

military_conflict = """
select DISTINCT ?result 
(GROUP_CONCAT(DISTINCT ?combatant1; SEPARATOR=",") AS ?combatants1)
(GROUP_CONCAT(DISTINCT ?combatant1Label; SEPARATOR=",") AS ?combatants1Label)
(GROUP_CONCAT(DISTINCT ?combatant2; SEPARATOR=",") AS ?combatants2)
(GROUP_CONCAT(DISTINCT ?combatant2Label; SEPARATOR=",") AS ?combatants2Label)
(GROUP_CONCAT(DISTINCT ?commander1; SEPARATOR=",") AS ?commanders1)
(GROUP_CONCAT(DISTINCT ?commander1Label; SEPARATOR=",") AS ?commanders1Label)
(GROUP_CONCAT(DISTINCT ?commander2; SEPARATOR=",") AS ?commanders2)
(GROUP_CONCAT(DISTINCT ?commander2Label; SEPARATOR=",") AS ?commanders2Label)
?strength1 ?strength2 ?casualties1 ?casualties2 ?causes where {{    
    OPTIONAL {{
        :{0} :result ?result
    }}
    
    OPTIONAL {{
        :{0} :combatant1 ?combatant1 .
        ?combatant1 rdfs:label ?combatant1Label
    }}
    
    OPTIONAL {{
        :{0} :combatant2 ?combatant2 .
        ?combatant2 rdfs:label ?combatant2Label
    }}
    
    OPTIONAL {{
        :{0} :commander1 ?commander1 .
        ?commander1 rdfs:label ?commander1Label
    }}
    
    OPTIONAL {{
        :{0} :commander2 ?commander2 .
        ?commander2 rdfs:label ?commander2Label
    }}
    
    OPTIONAL {{
        :{0} :strength1 ?strength1
    }}
    
    OPTIONAL {{
        :{0} :strength2 ?strength2
    }}
    
    OPTIONAL {{
        :{0} :casualties1 ?casualties1
    }}
    
    OPTIONAL {{
        :{0} :casualties2 ?casualties2
    }}
    
}} GROUP BY ?result ?strength1 ?strength2 ?casualties1 ?casualties2 ?causes
"""

military_person = """
select DISTINCT 
(GROUP_CONCAT(DISTINCT ?commands; SEPARATOR=",") AS ?commands)
(GROUP_CONCAT(DISTINCT ?commandsLabel; SEPARATOR=",") AS ?commandsLabel)
(GROUP_CONCAT(DISTINCT ?children; SEPARATOR=",") AS ?children)
(GROUP_CONCAT(DISTINCT ?childrenLabel; SEPARATOR=",") AS ?childrenLabel)
(GROUP_CONCAT(DISTINCT ?battles; SEPARATOR=",") AS ?battles)
(GROUP_CONCAT(DISTINCT ?battlesLabel; SEPARATOR=",") AS ?battlesLabel)
(GROUP_CONCAT(DISTINCT ?spouse; SEPARATOR=",") AS ?spouse)
(GROUP_CONCAT(DISTINCT ?spouseLabel; SEPARATOR=",") AS ?spouseLabel)
(GROUP_CONCAT(DISTINCT ?awards; SEPARATOR=",") AS ?awards)
?label ?religion ?laterwork ?birthname where {{    
    :{0} rdfs:label ?label
    OPTIONAL {{
        :{0} :religion ?religion 
        
    }}
    OPTIONAL {{
        :{0} :laterwork ?laterwork 
        
    }}
    OPTIONAL {{
        :{0} :birth_name ?birthname 
        
    }}
    OPTIONAL {{
        :{0} :awards ?awards 
        
    }}
    OPTIONAL {{
        :{0} :commands ?commands .
        ?commands rdfs:label ?commandsLabel
    }}
    OPTIONAL {{
        :{0} :spouse ?spouse .
        ?spouse rdfs:label ?spouseLabel
    }}
    OPTIONAL {{
        :{0} :children ?children .
        ?children rdfs:label ?childrenLabel
    }}
    
    OPTIONAL {{
        :{0} :battles ?battles .
        ?battles rdfs:label ?battlesLabel
    }}
    
    
}} GROUP BY ?label ?religion ?birthname ?laterwork
"""