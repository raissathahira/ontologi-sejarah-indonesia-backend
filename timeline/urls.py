from django.urls import path

from timeline.views import timeline, show_events, show_actors, homepage_actor, homepage_event, homepage_place, timeline_navbar

app_name = 'timeline'

urlpatterns = [
    path('', timeline),
    path('events/', show_events),
    path('actors/', show_actors),
    path('homepage/actor/', homepage_actor),
    path('homepage/event/', homepage_event),
    path('homepage/place/', homepage_place),
    path('navbar/', timeline_navbar),
]