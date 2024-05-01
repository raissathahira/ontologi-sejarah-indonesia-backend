from django.urls import path

from .views import *

app_name='graph'

urlpatterns = [
    path('uri/',uri_page,name="uri"),
    path('event',event,name="event"),
    path('image/<str:name>',get_image,name="wikidata"),
    
]