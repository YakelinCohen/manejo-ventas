from apps.ventas.services import VentaService
from apps.ventas.models import Cliente, EstadoVenta, MetodoPago, Venta
from apps.configuracion.models import Moneda
from apps.inventario.models import Producto

# Setup data
try:
    print("Setting up data...")
    cliente, _ = Cliente.objects.get_or_create(id_cliente=1, defaults={'nombre': 'Test', 'apellido': 'User'})
    producto, _ = Producto.objects.get_or_create(id_producto=1, defaults={'descripcion': 'Prod 1', 'precio': 100, 'unidades_stock': 100, 'costo': 50})
    moneda, _ = Moneda.objects.get_or_create(pk=1, defaults={'codigo': 'USD', 'nombre': 'Dolar'})
    metodo, _ = MetodoPago.objects.get_or_create(pk=1, defaults={'nombre': 'Efectivo'})
    
    # Ensure statuses exist
    pendiente, _ = EstadoVenta.objects.get_or_create(pk=1, defaults={'nombre': 'Pendiente'})
    pagada, _ = EstadoVenta.objects.get_or_create(pk=2, defaults={'nombre': 'Pagada'})
    EstadoVenta.objects.get_or_create(pk=3, defaults={'nombre': 'Completada'}) 

    # 1. Create a Sale with 0 payments initially (or partial) via Service
    # We use VentaService.crear_venta but pass empty payments to simulate "Credit" or just initial creation
    # But current crear_venta requires payment data list? No, it takes it but we can pass empty list?
    # Let's pass a small payment.
    
    print("Creating initial sale...")
    detalles = [{'producto_id': producto.id_producto, 'cantidad': 10}] # Total 1000
    pagos_iniciales = [{'metodo_pago_id': metodo.pk, 'monto': 200, 'moneda_id': moneda.pk}] # Paid 200
    
    venta = VentaService.crear_venta(
        cliente=cliente,
        detalles_data=detalles,
        pagos_data=pagos_iniciales,
        observacion="Partial Payment Sale"
    )
    
    print(f"Sale created. ID: {venta.pk}. Total: {venta.total}. Status ID: {venta.estado.pk} (Expect 1)")
    
    if venta.estado.pk != 1:
        print("ERROR: Initial status should be 1 (Pendiente)")
    else:
        print("Initial status OK.")

    # 2. Add another partial payment
    print("Adding partial payment of 300...")
    nuevos_pagos = [{'metodo_pago_id': metodo.pk, 'monto': 300, 'moneda_id': moneda.pk}]
    venta = VentaService.registrar_pago(venta.pk, nuevos_pagos)
    
    # Refresh from DB to be sure
    venta.refresh_from_db()
    total_pagado = sum(p.monto for p in venta.pagoventa_set.all())
    print(f"Total Paid: {total_pagado}. Status ID: {venta.estado.pk} (Expect 1)")
    
    if venta.estado.pk != 1:
        print("ERROR: Status updated prematurely.")
    
    # 3. Add remaining payment
    remaining = venta.total - total_pagado # 1000 - 500 = 500
    print(f"Adding remaining payment of {remaining}...")
    final_pago = [{'metodo_pago_id': metodo.pk, 'monto': float(remaining), 'moneda_id': moneda.pk}]
    venta = VentaService.registrar_pago(venta.pk, final_pago)
    
    venta.refresh_from_db()
    print(f"Final Status ID: {venta.estado.pk} (Expect 2)")
    
    if venta.estado.pk == 2:
        print("SUCCESS: Sale completed successfully.")
    else:
        print(f"ERROR: Sale status {venta.estado.pk} is not 2.")

except Exception as e:
    print(f"Test Failed: {e}")
    import traceback
    traceback.print_exc()
