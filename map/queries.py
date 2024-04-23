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
prefix geof: <http://www.opengis.net/def/function/geosparql/>
"""

get_all = """
select DISTINCT ?a ?label ?type where {
    ?a rdf:type ?type ;
    rdfs:label ?label .
    FILTER (?type IN ( sem:Event, sem:Actor, sem:Place, geo:Feature ))
}"""

get_search = """
select DISTINCT ?a ?label ?type ?summary where {{
    ?a rdf:type ?type ;
        rdfs:label ?label ;
        ?b ?c .
        
    OPTIONAL{{ 
      ?a ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.
    
    FILTER (?type IN ( sem:Event, sem:Actor, sem:Place ))
    FILTER (CONTAINS(LCASE(STR(?c)), LCASE("{0}")))
}}
ORDER BY ASC(?label)
LIMIT 10
OFFSET {1}
"""

get_total_search = """
select (COUNT(DISTINCT ?a) as ?count) where {{
    ?a rdf:type ?type ;
        rdfs:label ?label ;
        ?b ?c .
    FILTER (?type IN ( sem:Event, sem:Actor, sem:Place ))
    FILTER (CONTAINS(LCASE(STR(?c)), LCASE("{0}")))
}}
"""

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
    }}.
    
    OPTIONAL{{ 
      ?thing :wikiurl ?wikiurl .
    }}.
    
    OPTIONAL{{ 
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
    ?thing rdf:type	sem:Actor ;
    rdfs:label ?label;
    
    OPTIONAL{{ 
      ?thing :image ?image .
    }}.
    
    OPTIONAL{{ 
      ?thing :wikiurl ?wikiurl .
    }}.
    
    OPTIONAL{{ 
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
    }}.
    
    OPTIONAL{{ 
      ?thing :wikiurl ?wikiurl .
    }}.
    
    OPTIONAL{{ 
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

place = """
select DISTINCT ?label ?event ?eventLabel ?location ?lat ?lng

where {{
    :{0} rdf:type geo:Feature ;
        rdfs:label ?label ;
        geo:hasGeometry ?geometryA .
    
    ?geometryA geo:asWKT ?location ;
        :latitude ?lat ;
        :longitude ?lng .
    
    ?event rdf:type sem:Event ;
        rdfs:label ?eventLabel ;
        :location ?feature .
        
    ?feature geo:hasGeometry ?geometryB .
    ?geometryB geo:asWKT ?locationB
    
    FILTER(
        geof:sfContains(?location, ?locationB)
    )
    
}}

"""

actor = """
select DISTINCT ?label ?dateStart ?dateEnd

where {{
    :{0} rdfs:label ?label .
        
    optional {{    
    :{0} time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
    	time:hasEnd ?inst2 .
    }}
    
    optional {{
    ?inst1 time:inXSDDate ?dateStart .
    }}
    optional {{
    ?inst2 time:inXSDDate ?dateEnd .
    }}
    
    
}}
"""

conflict = """
select DISTINCT ?result 
(GROUP_CONCAT(DISTINCT ?side; SEPARATOR=",") AS ?side)
(GROUP_CONCAT(DISTINCT ?sideLabel; SEPARATOR=",") AS ?sideLabel)
(GROUP_CONCAT(DISTINCT ?leadfigure; SEPARATOR=",") AS ?leadfigure)
(GROUP_CONCAT(DISTINCT ?leadfigureLabel; SEPARATOR=",") AS ?leadfigureLabel)
?casualties ?causes where {{    
    OPTIONAL {{
        :{0} :result ?result
    }}
    
    OPTIONAL {{
        :{0} :side ?side .
        ?side rdfs:label ?sideLabel
    }}
    
    OPTIONAL {{
        :{0} :leadfigure ?leadfigure .
        ?leadfigure rdfs:label ?leadfigureLabel
    }}
    
    OPTIONAL {{
        :{0} :casualties ?casualties
    }}
    
    OPTIONAL {{
        :{0} :causes ?causes
    }}
    
}} GROUP BY ?result ?casualties ?causes
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

get_timeline_event_homepage = """
SELECT DISTINCT  ?baseURI ?thing ?label ?summary ?wikiurl ?image ?firstDate ?secondDate WHERE {{
    ?thing rdf:type	sem:Event ;
    rdfs:label ?label;
    OPTIONAL{{ 
      ?thing :image ?image .
    }}.
    
    OPTIONAL{{ 
      ?thing :wikiurl ?wikiurl .
    }}.
    
    OPTIONAL{{ 
      ?thing ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.

      ?thing time:hasTime ?tempEntity .
      ?tempEntity time:hasBeginning ?inst1 ;
                  time:hasEnd ?inst2 .

      ?inst1 time:inXSDDate ?firstDate .
      ?inst2 time:inXSDDate ?secondDate .
      
      BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .

    }} ORDER BY ?thing LIMIT 3
"""

get_timeline_actor_homepage = """
SELECT DISTINCT  ?baseURI ?thing ?label ?summary ?wikiurl ?image WHERE {{
    ?thing rdf:type	sem:Actor ;
    rdfs:label ?label;
    
    OPTIONAL{{ 
      ?thing :image ?image .
    }}.
    
    OPTIONAL{{ 
      ?thing :wikiurl ?wikiurl .
    }}.
    
    OPTIONAL{{ 
      ?thing ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.

    BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .

    }} ORDER BY ?thing LIMIT 3
"""

get_timeline_place_homepage = """
SELECT DISTINCT  ?baseURI ?thing ?label ?latitude ?longitude ?summary ?wikiurl ?image WHERE {{
    ?thing rdf:type	geo:Feature ;
    rdfs:label ?label;
    
    OPTIONAL{{ 
      ?thing :image ?image .
    }}.
    
    OPTIONAL{{ 
      ?thing :wikiurl ?wikiurl .
    }}.
    
    OPTIONAL{{ 
      ?thing ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.
    
    ?thing geo:hasGeometry ?geometry .
    ?geometry :latitude ?latitude;
        :longitude ?longitude.

    BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .

    }} ORDER BY ?thing LIMIT 3
"""