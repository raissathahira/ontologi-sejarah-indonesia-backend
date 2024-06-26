from django.urls import path

from .views import *

app_name='graph'

urlpatterns = [
    path('uri/',uri_page,name="uri"),
    path('event',event,name="event"),
    path('image/<str:name>',get_image,name="wikidata"), 
    path('alias/<str:name>',get_alias,name='wikidata_alias'),
    path('id/<str:name>',get_id,name='wikidata_id'),
    path('image2',no_image,name="no_image"),
    path('all',get_all2,name="all")
]