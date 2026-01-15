from django.urls import path
from apps.ventas.views import VentaView, ClienteView
urlpatterns = [
    path('ventas/', VentaView.as_view(), name='ventas'), 
    path('ventas/<int:id>/', VentaView.as_view(), name='venta-detalle'),
    path('ventas/crear/', VentaView.as_view(), name='crear-venta'),
    path('clientes/', ClienteView.as_view(), name='clientes'),
    path('clientes/<int:id>/', ClienteView.as_view(), name='cliente-detalle'),
    path('clientes/crear/', ClienteView.as_view(), name='crear-cliente'),

]