from django.urls import path
from .views import fetch_data, get_detail
app_name = 'map'

urlpatterns = [
    path('', fetch_data),
    path('detail/<str:iri>', get_detail)
]