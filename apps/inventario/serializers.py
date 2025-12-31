from rest_framework import serializers
from .models import Producto,Categoria,Estante,Nivel

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'  

class EstanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estante
        fields = '__all__'

class NivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nivel
        fields = '__all__'