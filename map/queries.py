military_conflict = """
select DISTINCT ?label ?result 
(GROUP_CONCAT(distinct ?combatant1; SEPARATOR=", ") AS ?combatants1) 
(GROUP_CONCAT(distinct ?combatant2; SEPARATOR=", ") AS ?combatants2)
(GROUP_CONCAT(distinct ?commander1; SEPARATOR=", ") AS ?commanders1)
(GROUP_CONCAT(distinct ?commander2; SEPARATOR=", ") AS ?commanders2)
?strength1 ?strength2 ?casualties1 ?casualties2 ?causes ?dateStart ?dateEnd ?location where {{
    :{0} rdfs:label ?label ;
        :location ?feature .
    
    OPTIONAL {{
        :{0} :result ?result
    }}
    
    OPTIONAL {{
        :{0} :combatant1 ?combatant1
    }}
    
    OPTIONAL {{
        :{0} :combatant2 ?combatant2
    }}
    
    OPTIONAL {{
        :{0} :commander1 ?commander1
    }}
    
    OPTIONAL {{
        :{0} :commander2 ?commander2
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
    
    :{0} time:hasTime ?tempEntity .
    ?tempEntity time:hasBeginning ?inst1 ;
    	time:hasEnd ?inst2 .
    
    ?inst1 time:inXSDDate ?dateStart .
    ?inst2 time:inXSDDate ?dateEnd .
    
    OPTIONAL {{ 
        ?feature geo:hasGeometry ?geometry .
    
        ?geometry geo:asWKT ?location .
    }}
}}
GROUP BY ?label ?result ?strength1 ?strength2 ?causes 
?casualties1 ?casualties2 ?dateStart ?dateEnd ?location
"""