from django.urls import path
from .views import fetch_map_data, fetch_all_data, get_detail
app_name = 'map'

urlpatterns = [
    path('', fetch_map_data),
    path('all', fetch_all_data),
    path('detail/<str:iri>', get_detail)
]