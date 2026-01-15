from django.db import transaction
from django.core.exceptions import ValidationError
from apps.ventas.models import Venta, DetalleVenta
from apps.inventario.models import Producto, Lote

class VentaService:
    
    @classmethod
    @transaction.atomic
    def crear_venta(cls, cliente, detalles_data, observacion=None):
        """
        Crea una venta completa, calculando totales y descontando stock
        priorizando lotes por vencer.
        
        :param cliente: Instancia de Cliente
        :param detalles_data: Lista de diccionarios [{'producto_id': 1, 'cantidad': 5}, ...]
        :param observacion: Texto opcional
        """
        total_venta = 0
        venta = Venta.objects.create(
            cliente=cliente,
            total=0, # Se actualiza al final
            observacion=observacion
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
