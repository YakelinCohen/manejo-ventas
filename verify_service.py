from apps.ventas.services import VentaService
from apps.ventas.models import Cliente, EstadoVenta, MetodoPago
from apps.configuracion.models import Moneda
from apps.inventario.models import Producto

# Setup data
try:
    cliente, _ = Cliente.objects.get_or_create(nombre="Test", apellido="User", defaults={'nombre': 'Test', 'apellido': 'User'})
    producto, _ = Producto.objects.get_or_create(id_producto=1, defaults={'descripcion': 'Prod 1', 'precio': 100, 'unidades_stock': 100, 'costo': 50})
    moneda, _ = Moneda.objects.get_or_create(pk=1, defaults={'codigo': 'USD', 'nombre': 'Dolar'})
    metodo, _ = MetodoPago.objects.get_or_create(pk=1, defaults={'nombre': 'Efectivo'})
    # Ensure EstadoVenta with id=3 exists (used in service)
    EstadoVenta.objects.get_or_create(pk=3, defaults={'nombre': 'Completada'})
    
    # Update stock for test
    producto.unidades_stock = 100
    producto.save()

    print("Data setup complete.")

    detalles = [{'producto_id': producto.id_producto, 'cantidad': 2}]
    pagos = [{'metodo_pago_id': metodo.pk, 'monto': 200, 'moneda_id': moneda.pk}]
    
    print("Calling crear_venta...")
    
    # Try with Client Instance (as per docstring)
    venta = VentaService.crear_venta(
        cliente=cliente,
        detalles_data=detalles,
        pagos_data=pagos,
        observacion="Test payment"
    )
    
    print(f"Venta created successfully: ID {venta.id_venta}, Total {venta.total}")
    
    # Verify Payment
    if venta.pagoventa_set.count() == 1:
        print("Payment record found.")
    else:
        print("ERROR: Payment record not found.")

except Exception as e:
    print(f"Test Failed: {e}")
    import traceback
    traceback.print_exc()
