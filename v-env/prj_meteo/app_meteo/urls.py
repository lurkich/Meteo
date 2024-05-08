
from django.urls import path
from app_meteo import views

from .views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('dashboard', dashboard, name='station meteo'),
]

