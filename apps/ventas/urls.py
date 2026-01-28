from django.urls import path
from apps.ventas.views import VentaView, ClienteView, MetodoPagoView, EstadoPagoView, PagoVentaView
urlpatterns = [
    path('ventas/', VentaView.as_view(), name='ventas'), 
    path('ventas/<int:id>/', VentaView.as_view(), name='venta-detalle'),
    path('ventas/crear/', VentaView.as_view(), name='crear-venta'),
    path('clientes/', ClienteView.as_view(), name='clientes'),
    path('clientes/<int:id>/', ClienteView.as_view(), name='cliente-detalle'),
    path('clientes/crear/', ClienteView.as_view(), name='crear-cliente'),
    path('metodos-pago/', MetodoPagoView.as_view(), name='metodos-pago'),
    path('metodos-pago/<int:id>/', MetodoPagoView.as_view(), name='metodo-pago-detalle'),
    path('metodos-pago/crear/', MetodoPagoView.as_view(), name='crear-metodo-pago'),
    path('estados-venta/', EstadoPagoView.as_view(), name='estados-venta'),
    path('estados-venta/<int:id>/', EstadoPagoView.as_view(), name='estado-venta-detalle'),
    path('estados-venta/crear/', EstadoPagoView.as_view(), name='crear-estado-venta'),
    path('pagos-venta/', PagoVentaView.as_view(), name='pagos-venta'),
    path('pagos-venta/<int:id>/', PagoVentaView.as_view(), name='pago-venta-detalle'),
    path('pagos-venta/agregar/', PagoVentaView.as_view(), name='agregar-pago-venta'),

]