from django.urls import path, include
from rest_framework import routers
from apps.configuracion.views import MonedaView, ActualizarTasaAPIView
 
urlpatterns = [
    path('monedas/', MonedaView.as_view(), name='monedas'),
    path('tasa/actualizar/', ActualizarTasaAPIView.as_view(), name='actualizar-tasa'),
]