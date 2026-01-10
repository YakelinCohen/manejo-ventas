from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import date
from apps.inventario.models import Producto, Lote, CodigoBarras

class ProductoService:
    """
    Servicio para manejar la lógica de negocio de Productos.
    Aquí los imports están arriba porque este archivo no define modelos.
    """

    @staticmethod
    def validar_datos_basicos(precio, lotes_data):
        if precio <= 0:
            raise ValidationError("El precio debe ser positivo.")
        
        hoy = date.today()
        for lote in lotes_data:
            if lote['fecha_vencimiento'] < hoy:
                raise ValidationError(f"El lote {lote['codigo']} ya está vencido.")

    @classmethod
    @transaction.atomic
    def crear_producto_completo(cls, **data):
        # 1. Extraer listas
        lotes_data = data.pop('lotes_data', []) or data.pop('lote_set', [])
        codigos_data = data.pop('codigos_barras_data', []) or data.pop('codigobarras_set', [])

        # 2. Validar
        cls.validar_datos_basicos(data.get('precio'), lotes_data)

        # 3. Crear Producto
        producto = Producto.objects.create(**data)

        # 4. Optimización: BULK CREATE para Códigos de Barras
        if codigos_data:
            codigos_objs = [
                CodigoBarras(producto=producto, codigo=c['codigo']) 
                for c in codigos_data
            ]
            CodigoBarras.objects.bulk_create(codigos_objs)

        # 5. Optimización: BULK CREATE para Lotes
        if lotes_data:
            lotes_objs = [
                Lote(
                    producto=producto,
                    codigo=l['codigo'],
                    fecha_expedicion=l['fecha_expedicion'],
                    fecha_vencimiento=l['fecha_vencimiento'],
                    cantidad_disponible=l['cantidad_disponible']
                ) for l in lotes_data
            ]
            Lote.objects.bulk_create(lotes_objs)

        return producto