from django.urls import path
from .views import Estantes, Productos,CategoriaProductos, Categorias

urlpatterns = [
    path('productos/', Productos.as_view(), name='productos'), 
    path('categorias/', Categorias.as_view(), name='categorias'),
    path('categorias/<int:categoria_id>/productos/', CategoriaProductos.as_view(), name='categoria-productos'),
    path('estantes/', Estantes.as_view(), name='estantes'),
]