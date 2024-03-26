from django.urls import path

from timeline.views import fetch_data, location

app_name = 'timeline'

urlpatterns = [
    path('', fetch_data),
    path('location/<str:name>/', location)
]