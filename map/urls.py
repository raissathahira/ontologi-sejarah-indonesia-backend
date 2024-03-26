from django.urls import path
from .views import fetch_data
app_name = 'map'

urlpatterns = [
    path('', fetch_data)
]