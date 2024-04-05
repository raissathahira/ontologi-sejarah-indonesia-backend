from django.urls import path

from timeline.views import timeline, show_events

app_name = 'timeline'

urlpatterns = [
    path('', timeline),
    path('events/', show_events),

]