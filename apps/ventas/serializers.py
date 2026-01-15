from rest_framework import serializers
from apps.ventas.models import Cliente, Venta, DetalleVenta
from apps.inventario.models import Producto

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class DetalleVentaSerializer(serializers.ModelSerializer): 
     
    class ProductoVentaSerializer(serializers.ModelSerializer):
         
         class Meta:
             model = Producto
             fields = ['id_producto', 'descripcion', 'precio']

    producto = ProductoVentaSerializer()


    class Meta:
        model = DetalleVenta
        fields = ['id_detalle_venta', 'cantidad', 'precio_unitario', 'producto']


class VentaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    detalles_venta = DetalleVentaSerializer(many=True, source='detalleventa_set')

    class Meta:
        model = Venta
        fields = ['id_venta', 'fecha_venta', 'total', 'cliente', 'observacion', 'detalles_venta']