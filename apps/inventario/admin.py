from django.contrib import admin
from .models import Producto

# @admin.register(Producto)
# class ProductoAdmin(admin.ModelAdmin):
#     list_display = ('id_producto', 'descripcion', 'precio', 'unidades', 'fecha_creacion', 'fecha_actualizacion') # Columnas que verás
#     search_fields = ('descripcion',) # Buscador por descripción