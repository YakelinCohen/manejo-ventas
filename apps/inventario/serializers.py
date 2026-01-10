from rest_framework import serializers
from apps.inventario.models  import Lote, Producto,Categoria,Estante,Nivel

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ProductoCreateSerializer(serializers.ModelSerializer):
    class CodigoBarrasSerializer(serializers.Serializer):
        codigo = serializers.CharField(max_length=100)
    
    class LoteSerializer(serializers.Serializer):
        codigo = serializers.CharField(max_length=100)
        fecha_expedicion = serializers.DateField()
        fecha_vencimiento = serializers.DateField()
        cantidad_disponible = serializers.IntegerField() 

    # Renombramos para coincidir con los argumentos del Manager (codigos_barras_data, lotes_data)
    # Usamos source='...' para leer la relación inversa desde el modelo al responder
    codigos_barras_data = CodigoBarrasSerializer(many=True, source='codigobarras_set')
    lotes_data = LoteSerializer(many=True, required=False, source='lote_set') 
    
    class Meta:
        model = Producto
        fields = ['id_producto', 'descripcion', 'precio', 'cantidad_min_exhibicion',
                  'cantidad_max_exhibicion', 'unidades_en_exhibicion', 'requiere_lotes',
                  'categoria', 'nivel', 'fecha_creacion', 'fecha_actualizacion',
                  'codigos_barras_data', 'lotes_data']
        read_only_fields = ('id_producto', 'fecha_creacion', 'fecha_actualizacion')


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

class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = '__all__'