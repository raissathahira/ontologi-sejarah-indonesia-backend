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
select DISTINCT ?a ?label ?type where {{
    ?a rdf:type ?type ;
    rdfs:label ?label .
    
    FILTER (?type IN ( sem:Event, sem:Actor, geo:Feature ))
}}"""

get_search = """
select DISTINCT ?a ?label ?type ?summary where {{
    ?a rdf:type ?type ;
        rdfs:label ?label ;
        ?b ?c .
        
    OPTIONAL {{ 
        ?a ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.
    
    OPTIONAL{{
      ?a rdfs:seeAlso ?version. 
      ?version ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.
    
    FILTER (?type IN ( sem:Event, sem:Actor, sem:Place ))
    FILTER (CONTAINS(LCASE(STR(?c)), LCASE("{0}")))
    BIND(IF(LCASE(STR(?label)) = LCASE(("{0}")), 0, 1) AS ?priority)
}}
ORDER BY ?priority ASC(?label)
LIMIT 10
OFFSET {1}}
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
select DISTINCT ?event ?label ?lat ?lon ?yearStart where {{
    ?event rdf:type sem:Event ;
        rdfs:label ?label ;
        rdfs:seeAlso ?version .

    ?version rdf:type sem:View ;
        :hasLocation ?feature .

    ?feature geo:hasGeometry ?geometry .
    ?geometry :latitude ?lat ;
        :longitude ?lon .

    ?version time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 .
    ?inst1 time:inDateTime ?dateTime .
    ?dateTime time:year ?yearStart .
}}
"""

get_types = """
select DISTINCT 
(GROUP_CONCAT(distinct ?typeLabel; SEPARATOR=",") as ?typeLabels)
where {{
    :{0} rdf:type ?type .
    ?type rdfs:label ?typeLabel .
}}
"""

get_timeline_event = """
SELECT DISTINCT  ?baseURI ?thing ?label ?summary ?wikiurl ?image ?firstDateDay ?firstDateMonth ?firstDateYear ?secondDateDay ?secondDateMonth ?secondDateYear WHERE {{
    ?thing rdfs:seeAlso ?version;
        rdfs:label ?label;
        rdf:type sem:Event.
        
    ?version rdf:type sem:View.

    OPTIONAL{{ 
      ?version :image ?image .
    }}.
    
    OPTIONAL{{ 
      ?version :wikiurl ?wikiurl .
    }}.
    
    OPTIONAL{{ 
      ?version ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.

    ?version time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
                time:hasEnd ?inst2 .
        
    	OPTIONAL {{?inst1 time:inDateTime ?firstDate .}}
        OPTIONAL {{?firstDate time:day ?firstDateDay.}}
        OPTIONAL {{?firstDate time:month ?firstDateMonth.}}
        OPTIONAL {{?firstDate time:year ?firstDateYear.}}

        OPTIONAL {{?inst2 time:inDateTime ?secondDate .}}
        OPTIONAL {{?secondDate time:day ?secondDateDay.}}
        OPTIONAL {{?secondDate time:month ?secondDateMonth.}}
        OPTIONAL {{?secondDate time:year ?secondDateYear.}}
      
    BIND(REPLACE(STR(?version), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .
    FILTER(?label = "{0}")  .

    }} ORDER BY ?thing
"""

get_timeline_navbar = """
SELECT DISTINCT  ?baseURI ?thing ?label ?summary ?wikiurl ?image ?firstDateDay ?firstDateMonth ?firstDateYear ?secondDateDay ?secondDateMonth ?secondDateYear WHERE {{
    ?thing rdfs:seeAlso ?version;
        rdfs:label ?label;
        rdf:type sem:Event.
        
    ?version rdf:type sem:View.

    OPTIONAL{{ 
      ?version :image ?image .
    }}.
    
    OPTIONAL{{ 
      ?version :wikiurl ?wikiurl .
    }}.
    
    OPTIONAL{{ 
      ?version ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).
    }}.

    ?version time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
                time:hasEnd ?inst2 .
        
    	OPTIONAL {{?inst1 time:inDateTime ?firstDate .}}
        OPTIONAL {{?firstDate time:day ?firstDateDay.}}
        OPTIONAL {{?firstDate time:month ?firstDateMonth.}}
        OPTIONAL {{?firstDate time:year ?firstDateYear.}}

        OPTIONAL {{?inst2 time:inDateTime ?secondDate .}}
        OPTIONAL {{?secondDate time:day ?secondDateDay.}}
        OPTIONAL {{?secondDate time:month ?secondDateMonth.}}
        OPTIONAL {{?secondDate time:year ?secondDateYear.}}
      
    BIND(REPLACE(STR(?version), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .

    }} ORDER BY ?thing
"""

get_timeline_navbar_actors = """
SELECT DISTINCT  ?baseURI ?thing ?label ?summary ?wikiurl ?image WHERE {{
    ?thing rdf:type	sem:Actor ;
    rdfs:label ?label;
    
    OPTIONAL{{ 
      ?thing :image ?image .
    }}.
    
    ?thing :wikiurl ?wikiurl .
    
    ?thing ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).

    BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .

    }} ORDER BY ?thing LIMIT 30
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
    FILTER(?label = "{0}") .

    }} ORDER BY ?thing
"""

get_timeline_place = """
SELECT DISTINCT  ?baseURI ?thing ?label ?latitude ?longitude ?summary ?location ?wikiurl ?image WHERE {{
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
    
    OPTIONAL{{ 
      ?thing geo:hasGeometry ?geometry .
      ?geometry :latitude ?latitude ;
              :longitude ?longitude ;
               geo:asWKT ?location
    }}.

    BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .
    FILTER(?label = "{0}")  .

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
select DISTINCT ?label ?authorityLabel ?summary ?image ?wikiurl
?dayStart ?monthStart ?yearStart
?dayEnd ?monthEnd ?yearEnd
(GROUP_CONCAT(DISTINCT ?location; SEPARATOR="|") AS ?location)
(GROUP_CONCAT(DISTINCT ?actor; SEPARATOR=",") AS ?actor)
(GROUP_CONCAT(DISTINCT ?actorLabel; SEPARATOR=",") AS ?actorLabel)
(GROUP_CONCAT(DISTINCT ?person; SEPARATOR=",") AS ?person)
(GROUP_CONCAT(DISTINCT ?personLabel; SEPARATOR=",") AS ?personLabel)
(GROUP_CONCAT(DISTINCT ?feature; SEPARATOR=",") AS ?feature)
(GROUP_CONCAT(DISTINCT ?featureLabel; SEPARATOR=",") AS ?featureLabel)
where {{    
    :{0} rdf:type sem:Event ;
    rdfs:label ?label ;
    rdfs:seeAlso ?version .
    
    ?version rdf:type sem:View .
    ?version sem:accordingTo ?authority .
    ?authority rdfs:label ?authorityLabel
    
    OPTIONAL {{
        ?version :hasLocation ?feature .
        ?feature rdfs:label ?featureLabel .
        
        OPTIONAL {{
            ?feature geo:hasGeometry ?geometry .
            ?geometry geo:asWKT ?location .
        }}    
    }}
    
    OPTIONAL {{
        ?version :wikiurl ?wikiurl .
    }}
    
    OPTIONAL {{
        ?version time:hasTime ?tempEntity .
        
        OPTIONAL {{
            ?tempEntity time:hasBeginning ?instStart .
            ?instStart time:inDateTime ?dateTime .
        
        	OPTIONAL {{
                ?dateTime time:year ?yearStart .
        	}}
                 
            OPTIONAL {{
                ?dateTime time:month ?monthStart .
            }}
            
            OPTIONAL {{                
                ?dateTime time:day ?dayStart .
            }}        
        }}
                
        OPTIONAL {{
            ?tempEntity time:hasEnd ?instEnd .
            ?instEnd time:inDateTime ?dateTimeEnd .

            OPTIONAL {{
                ?dateTimeEnd time:year ?yearEnd .
            }}
            
            OPTIONAL {{
                ?dateTimeEnd time:month ?monthEnd .
            }}
            
            OPTIONAL {{
                ?dateTimeEnd time:day ?dayEnd .
            }}
        }}    
    }}
    
    OPTIONAL {{
        ?version sem:hasActor ?actor .
        ?actor rdfs:label ?actorLabel .
    }}
    
    MINUS {{ 
        ?actor rdf:type foaf:Person .
    }}
    
    OPTIONAL {{
        ?version sem:hasActor ?person .
        ?person rdfs:label ?personLabel ;
            rdf:type foaf:Person .
    }}
        
    OPTIONAL {{
        ?version dc:description ?summary .
    }}
        
    OPTIONAL {{
        ?version :image ?image .
    }} 
    
}} GROUP BY ?label ?authorityLabel ?summary ?image ?wikiurl
?dayStart ?monthStart ?yearStart
?dayEnd ?monthEnd ?yearEnd
"""

place = """
select DISTINCT ?label ?event ?eventLabel ?location ?lat ?lng ?summary ?wikiurl
where {{
    :{0} rdf:type geo:Feature ;
        rdfs:label ?label ;
        
    OPTIONAL {{
        :{0} :wikiurl ?wikiurl
    }}
    
    OPTIONAL {{
        :{0} geo:hasGeometry ?geometryA .
        
        ?geometryA geo:asWKT ?location ;
            :latitude ?lat ;
            :longitude ?lng .
            
        ?event rdf:type sem:Event ;
            rdfs:label ?eventLabel ;
            rdfs:seeAlso ?version .
        
        ?version :hasLocation ?feature .
        ?feature geo:hasGeometry ?geometryB .
        ?geometryB geo:asWKT ?locationB
        
        FILTER(
            geof:sfContains(?location, ?locationB)
        )
    }}
    
    OPTIONAL {{
        :{0} dc:description ?summary .
    }}
    
}}
"""

actor = """
select DISTINCT ?label ?image ?summary ?wikiurl
?dayStart ?monthStart ?yearStart
?dayEnd ?monthEnd ?yearEnd
(GROUP_CONCAT(DISTINCT ?event; SEPARATOR=",") AS ?event)
(GROUP_CONCAT(DISTINCT ?eventLabel; SEPARATOR=",") AS ?eventLabel)
where {{    
    :{0} rdfs:label ?label .
    
    OPTIONAL {{
        :{0} dc:description ?summary .
    }}
    
    OPTIONAL {{
        :{0} :wikiurl ?wikiurl .
    }}
    
    OPTIONAL {{
        :{0} time:hasTime ?tempEntity .
        
        OPTIONAL {{
            ?tempEntity time:hasBeginning ?instStart .
            ?instStart time:inDateTime ?dateTime .
        
        	OPTIONAL {{
                ?dateTime time:year ?yearStart .
        	}}
                 
            OPTIONAL {{
                ?dateTime time:month ?monthStart .
            }}
            
            OPTIONAL {{                
                ?dateTime time:day ?dayStart .
            }}        
        }}
                
        OPTIONAL {{
            ?tempEntity time:hasEnd ?instEnd .
            ?instEnd time:inDateTime ?dateTimeEnd .

            OPTIONAL {{
                ?dateTimeEnd time:year ?yearEnd .
            }}
            
            OPTIONAL {{
                ?dateTimeEnd time:month ?monthEnd .
            }}
            
            OPTIONAL {{
                ?dateTimeEnd time:day ?dayEnd .
            }}
        }}    
    }}
    
    OPTIONAL {{
        :{0} :image ?image .
    }}
    
    OPTIONAL {{
        :{0} :isActorOf ?version .
        ?event rdfs:seeAlso ?version .
        ?event rdf:type sem:Event ;
            rdfs:label ?eventLabel .
    }}    
}}
GROUP BY ?label ?image ?summary ?wikiurl
?dayStart ?monthStart ?yearStart
?dayEnd ?monthEnd ?yearEnd
"""

person = """
select DISTINCT
(GROUP_CONCAT(DISTINCT ?parent; SEPARATOR=",") AS ?parents)
(GROUP_CONCAT(DISTINCT ?parentLabel; SEPARATOR=",") AS ?parentsLabel)
(GROUP_CONCAT(DISTINCT ?children; SEPARATOR=",") AS ?children)
(GROUP_CONCAT(DISTINCT ?childrenLabel; SEPARATOR=",") AS ?childrenLabel)
(GROUP_CONCAT(DISTINCT ?relative; SEPARATOR=",") AS ?relative)
(GROUP_CONCAT(DISTINCT ?relativeLabel; SEPARATOR=",") AS ?relativeLabel)
where {{
    OPTIONAL {{
        :{0} :hasParent ?parent .
        ?parent rdfs:label ?parentLabel .
    }}

    OPTIONAL {{
        :{0} :hasChild ?children .
        ?children rdfs:label ?childrenLabel
    }}
    
    OPTIONAL {{
        :{0} :hasRelative ?relative .
        ?relative rdfs:label ?relativeLabel
    }}
}}
"""

get_timeline_event_homepage = """
SELECT DISTINCT  ?baseURI ?thing ?label ?summary WHERE {{
    ?thing rdfs:seeAlso ?version;
        rdfs:label ?label;
        rdf:type sem:Event.
        
    ?version rdf:type sem:View;
        ?predicate ?summary ;
	        FILTER(?predicate IN (:summary, dc:description)).
	    
    BIND(REPLACE(STR(?version), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .

    }} ORDER BY ?thing LIMIT 3
"""

get_timeline_actor_homepage = """
SELECT DISTINCT  ?baseURI ?thing ?label ?summary ?wikiurl ?image WHERE {{
    ?thing rdf:type	sem:Actor ;
    rdfs:label ?label;
    :image ?image;
    :wikiurl ?wikiurl; 
    ?predicate ?summary ;
	    FILTER(?predicate IN (:summary, dc:description)).

    BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .

    }} ORDER BY ?thing LIMIT 3
"""

get_timeline_place_homepage = """
SELECT ?baseURI ?thing (SAMPLE(?latitude) AS ?latitude) (SAMPLE(?label) AS ?label) (SAMPLE(?longitude) AS ?longitude) (SAMPLE(?location) AS ?location) WHERE {
    ?thing rdf:type geo:Feature ;
           rdfs:label ?label.

    ?thing geo:hasGeometry ?geometry .
    ?geometry :latitude ?latitude ;
              :longitude ?longitude ;
              geo:asWKT ?location .

    BIND(REPLACE(STR(?thing), "([^:/]+://[^/]+/).*", "$1") AS ?baseURI) .
}}GROUP BY ?baseURI ?thing
ORDER BY ?thing
LIMIT 3
"""
