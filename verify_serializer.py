from apps.ventas.serializers import VentaCreateSerializer
from apps.ventas.models import Cliente, EstadoVenta, MetodoPago
from apps.configuracion.models import Moneda
from apps.inventario.models import Producto

# Setup data
try:
    cliente, _ = Cliente.objects.get_or_create(id_cliente=1, defaults={'nombre': 'Test', 'apellido': 'User'})
    producto, _ = Producto.objects.get_or_create(id_producto=1, defaults={'descripcion': 'Prod 1', 'precio': 100, 'unidades_stock': 100, 'costo': 50})
    moneda, _ = Moneda.objects.get_or_create(pk=1, defaults={'codigo': 'USD', 'nombre': 'Dolar'})
    metodo, _ = MetodoPago.objects.get_or_create(pk=1, defaults={'nombre': 'Efectivo'})
    EstadoVenta.objects.get_or_create(pk=3, defaults={'nombre': 'Completada'})
    
    # Update stock for test
    producto.unidades_stock = 100
    producto.save()

    payload = {
        "cliente": cliente.id_cliente,
        "observacion": "Test serializer",
        "detalles": [
            {'producto_id': producto.id_producto, 'cantidad': 2}
        ],
        "pagos": [
            {'metodo_pago_id': metodo.pk, 'monto': 200, 'moneda_id': moneda.pk}
        ]
    }

    print("Validating with VentaCreateSerializer...")
    validador = VentaCreateSerializer(data=payload)
    if validador.is_valid():
        print("Validation successful!")
        print("Validated Data:", validador.validated_data)
        
        # Simulate View Logic
        data = validador.validated_data
        # Note: In Django view logic, Cliente.objects.get would be used. 
        # Here we just check the output structure.
        if data['cliente'] == cliente.id_cliente and len(data['detalles']) == 1:
            print("Serializer output structure correct.")
        else:
             print("Serializer output mismatch.")
    else:
        print("Validation Failed:", validador.errors)

except Exception as e:
    print(f"Test Failed: {e}")
    import traceback
    traceback.print_exc()
