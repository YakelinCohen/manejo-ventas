from rest_framework import serializers
from apps.ventas.models import Cliente, Venta, DetalleVenta,MetodoPago, EstadoVenta, PagoVenta
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


class PagoVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoVenta
        fields = ['monto', 'metodo_pago', 'moneda']

class VentaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    detalles_venta = DetalleVentaSerializer(many=True, source='detalleventa_set')
    pagos = PagoVentaSerializer(many=True, source='pagoventa_set')

    class Meta:
        model = Venta
        fields = ['id_venta', 'fecha_venta', 'total', 'cliente', 'observacion', 'detalles_venta', 'pagos']


# Serializer especifico para CREACION (Input)
class VentaCreateSerializer(serializers.Serializer):
    cliente = serializers.IntegerField()
    observacion = serializers.CharField(required=False, allow_blank=True)
    detalles = serializers.ListField(child=serializers.DictField())
    pagos = serializers.ListField(child=serializers.DictField())

    def validate_cliente(self, value):
        if not Cliente.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Cliente no existe")
        return value

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = '__all__'

class EstadoVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoVenta
        fields = '__all__'

class PagoVentaSerializer(serializers.ModelSerializer):
    venta = serializers.IntegerField()
    metodo_pago = serializers.IntegerField()
    moneda = serializers.IntegerField() 
    class Meta:
        model = PagoVenta
        fields = ['id_pago_venta', 'venta', 'monto', 'metodo_pago', 'moneda']