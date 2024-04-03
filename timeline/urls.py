from django.urls import path

from timeline.views import fetch_data_event, fetch_data_person, location

app_name = 'timeline'

urlpatterns = [
    path('event/', fetch_data_event),
    path('person/', fetch_data_person),
    path('location/<str:name>/', location),

]