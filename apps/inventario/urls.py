from django.urls import path
from apps.inventario.views import Productos, Categorias, CategoriaProductos, Estantes, AlertaVencimiento, Lotes
urlpatterns = [
    path('productos/', Productos.as_view(), name='productos'), 
    path('categorias/', Categorias.as_view(), name='categorias'),
    path('categorias/<int:categoria_id>/productos/', CategoriaProductos.as_view(), name='categoria-productos'),
    path('estantes/', Estantes.as_view(), name='estantes'),
    path('alertas/vencimientos/', AlertaVencimiento.as_view(), name='alertas-vencimiento'),
    path('lotes/', Lotes.as_view(), name='lotes')
]