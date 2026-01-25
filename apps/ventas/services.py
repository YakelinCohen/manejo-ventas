from django.db import transaction
from django.core.exceptions import ValidationError
from apps.ventas.models import Venta, DetalleVenta, EstadoVenta, PagoVenta, MetodoPago
from apps.inventario.models import Producto, Lote
from apps.configuracion.models import Moneda

class VentaService:
    
    @classmethod
    @transaction.atomic
    def crear_venta(cls, cliente, detalles_data, pagos_data, observacion=None):
        """
        Crea una venta completa, calculando totales y descontando stock
        priorizando lotes por vencer.
        
        :param cliente: Instancia de Cliente
        :param detalles_data: Lista de diccionarios [{'producto_id': 1, 'cantidad': 5}, ...]
        :param pagos_data: Lista [{'metodo_pago_id': 1, 'monto': 100, 'moneda_id': 1}, ...]
        :param observacion: Texto opcional
        """
        total_venta = 0
        estado_inicial = EstadoVenta.objects.get(id_estado_venta=3) 
        venta = Venta.objects.create(
            cliente=cliente,
            total=0.00, # Se actualiza al final
            observacion=observacion,
            estado=estado_inicial
        )

        for item in detalles_data:
            producto_id = item.get('producto_id')
            cantidad_solicitada = int(item.get('cantidad'))
            
            if cantidad_solicitada <= 0:
                raise ValidationError(f"La cantidad para el producto ID {producto_id} debe ser mayor a 0.")

            # Bloqueamos el registro para evitar condiciones de carrera
            producto = Producto.objects.select_for_update().get(pk=producto_id)
            
            # 1. Validar y Descontar Stock (Lógica FEFO)
            cls._descontar_stock(producto, cantidad_solicitada)

            # 2. Crear Detalle de Venta
            subtotal = producto.precio * cantidad_solicitada
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad_solicitada,
                precio_unitario=producto.precio
            )
            
            total_venta += subtotal

        # Actualizar total de la venta cabecera
        venta.total = total_venta
        venta.save()

        # 2. Registrar Pagos
        total_pagado = 0
        for pago in pagos_data:
            metodo = MetodoPago.objects.get(pk=pago['metodo_pago_id'])
            moneda = Moneda.objects.get(pk=pago['moneda_id'])
            monto = float(pago['monto'])
            
            PagoVenta.objects.create(
                venta=venta,
                monto=monto,
                metodo_pago=metodo,
                moneda=moneda
            )
            total_pagado += monto
            
        # Opcional: Validar que el pago cubra el total
        # Opcional: Validar que el pago cubra el total
        # Asegúrate de usar los IDs correctos para tus estados
        if total_pagado < total_venta:
            # Estado Pendiente/Incompleto
             venta.estado = EstadoVenta.objects.get(pk=1) 
        else:
            # Estado Pagado/Completo
            venta.estado = EstadoVenta.objects.get(pk=2)
        
        venta.save()
        return venta

    @classmethod
    @transaction.atomic
    def registrar_pago(cls, venta_id, pagos_data, observacion=None):
        """
        Registra un nuevo pago a una venta existente.
        Actualiza el estado de la venta si se completa el pago.
        """
        try:
        # 1. Bloqueo de fila para evitar condiciones de carrera
            venta = Venta.objects.select_for_update().get(pk=venta_id)
            if not venta.tiene_pago_pendiente:
                raise ValidationError(f"La venta {venta_id} ya está pagada.")
        except Venta.DoesNotExist:
            raise ValidationError(f"La venta {venta_id} no existe.")

    # 2. VALIDACIÓN DE MÉTODOS Y MONEDAS (Evita el bucle N+1)
    metodo_ids = [dato_pago['metodo_pago_id'] for dato_pago in pagos_data]
    moneda_ids = [dato_pago['moneda_id'] for dato_pago in pagos_data]
    
    # Verificamos cuántos existen de los solicitados
    metodos_existentes = MetodoPago.objects.filter(id__in=metodo_ids)
    monedas_existentes = Moneda.objects.filter(id__in=moneda_ids)

    if metodos_existentes.count() != len(set(metodo_ids)):
        raise ValidationError("Uno o más métodos de pago no son válidos.")
    
    if monedas_existentes.count() != len(set(moneda_ids)):
        raise ValidationError("Uno o más tipos de moneda no son válidos.")

    # Convertimos a diccionarios para acceso rápido
    dict_metodos = {metodo.id: metodo for metodo in metodos_existentes}
    dict_monedas = {moneda.id: moneda for moneda in monedas_existentes}

    # 3. REGISTRO DE PAGOS (Bulk Create es opcional aquí, pero útil)
    pagos_a_crear = []
    for pago in pagos_data:
        pagos_a_crear.append(PagoVenta(
            venta=venta,
            monto=Decimal(str(pago['monto'])), # Usar Decimal siempre
            metodo_pago=dict_metodos[pago['metodo_pago_id']],
            moneda=dict_monedas[pago['moneda_id']]
        ))
    
    PagoVenta.objects.bulk_create(pagos_a_crear)

    # 4. CÁLCULO OPTIMIZADO DEL TOTAL
    # Dejamos que la base de datos haga la suma, es mucho más rápido
    resultado = venta.pagoventa_set.aggregate(total_acumulado=Sum('monto'))
    total_acumulado = resultado['total_acumulado'] or Decimal('0.00')

    # 5. ACTUALIZACIÓN DE ESTADO (Usando constantes o IDs fijos)
    ID_PAGADA = 2
    ID_PENDIENTE = 1
    
    nuevo_estado_id = ID_PAGADA if total_acumulado >= venta.total else ID_PENDIENTE
    
    if venta.estado_id != nuevo_estado_id:
        venta.estado_id = nuevo_estado_id
        venta.save(update_fields=['estado']) # Solo actualizamos el campo estado por eficiencia
                
        return venta

    @staticmethod
    def _descontar_stock(producto, cantidad_a_descontar):
        """
        Descuenta stock. Si el producto usa lotes, busca los más próximos a vencer.
        """
        if not producto.requiere_lotes:
            if producto.unidades_stock < cantidad_a_descontar:
                raise ValidationError(f"Stock insuficiente para '{producto.descripcion}'. Disponible: {producto.unidades_stock}")
            producto.unidades_stock -= cantidad_a_descontar
            producto.save()
        else:
            lotes = Lote.objects.filter(producto=producto, cantidad_disponible__gt=0).order_by('fecha_vencimiento').select_for_update()
            stock_total = sum(l.cantidad_disponible for l in lotes)
            
            if stock_total < cantidad_a_descontar:
                raise ValidationError(f"Stock insuficiente en lotes para '{producto.descripcion}'. Solicitado: {cantidad_a_descontar}, Disponible: {stock_total}")

            cantidad_pendiente = cantidad_a_descontar
            for lote in lotes:
                if cantidad_pendiente <= 0: break
                tomar = min(lote.cantidad_disponible, cantidad_pendiente)
                lote.cantidad_disponible -= tomar
                lote.save()
                cantidad_pendiente -= tomar
