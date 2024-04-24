from django.urls import path

from timeline.views import timeline, show_events, homepage_actor, homepage_event, homepage_place

app_name = 'timeline'

urlpatterns = [
    path('', timeline),
    path('events/', show_events),
    path('homepage/actor/', homepage_actor),
    path('homepage/event/', homepage_event),
    path('homepage/place/', homepage_place),

]